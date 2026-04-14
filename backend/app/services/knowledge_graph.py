import httpx
import logging
from typing import List, Dict, Optional
# spacy imported lazily inside load_ner_model to speed up server startup
from SPARQLWrapper import SPARQLWrapper, JSON
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class KnowledgeGraphVerifier:
    """
    Knowledge graph verification using Wikidata and Google Fact Check
    
    Features:
    - Named Entity Recognition (spaCy multilingual)
    - Wikidata SPARQL queries for entity verification
    - Google Fact Check API integration
    - Smart quota management to preserve API limits
    - Caching of results
    """
    
    def __init__(self, google_api_key: Optional[str] = None):
        self.google_api_key = google_api_key
        self.nlp = None
        self._nlp_loaded = False  # Track if we've attempted to load
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        self.google_factcheck_endpoint = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        
        # Quota tracking
        self.google_api_calls_today = 0
        self.google_api_limit_daily = 1000
        self.last_reset = datetime.now()
        
        # NER model loads lazily on first use (not at startup)
        
    def load_ner_model(self):
        """Load spaCy multilingual NER model"""
        try:
            import spacy  # Lazy import
            self.nlp = spacy.load("xx_ent_wiki_sm")
            logger.info("✅ Loaded spaCy multilingual NER model")
        except Exception as e:
            logger.warning(f"⚠️ Could not load spaCy model: {e}")
            logger.info("Install with: python -m spacy download xx_ent_wiki_sm")
            self.nlp = None
    
    async def verify_claim(self, text: str, language: str = "en", confidence: float = 0.5) -> Dict:
        """
        Verify claim using knowledge graph sources
        
        Args:
            text: Text to verify
            language: Language code (ISO 639-1)
            confidence: Current ML confidence (used for smart routing)
            
        Returns:
            Verification results with sources and adjusted confidence
        """
        results = {
            "entities": [],
            "fact_checks": [],
            "sources": [],
            "knowledge_confidence": 0.5,
            "wikidata_verified": False,
            "google_verified": False
        }
        
        # Reset daily quota if needed
        self._check_and_reset_quota()
        
        # 1. Extract named entities
        entities = self.extract_entities(text)
        results["entities"] = entities
        logger.info(f"Extracted {len(entities)} entities")
        
        # 2. Query Wikidata for entity verification (always free, no quota)
        if entities:
            wikidata_tasks = [
                self.wikidata_lookup(entity["text"], language)
                for entity in entities[:3]  # Top 3 entities
            ]
            wikidata_results = await asyncio.gather(*wikidata_tasks, return_exceptions=True)
            
            for result in wikidata_results:
                if isinstance(result, dict) and result:
                    results["sources"].append({
                        "name": "Wikidata",
                        "url": result.get("url", ""),
                        "info": result.get("description", ""),
                        "label": result.get("label", "")
                    })
                    results["wikidata_verified"] = True
        
        # ------------------------------------------------------------------
        # SEMANTIC VERIFICATION STRATEGY
        # ------------------------------------------------------------------
        # Priority 1: Google Fact Check (understands CLAIMS and RELATIONSHIPS)
        # Priority 2: Wikidata (only verifies ENTITY EXISTENCE, not relationships)
        # 
        # CRITICAL: Wikidata alone is NOT sufficient for claim verification!
        # Example: "India is capital of USA" 
        #   - Wikidata finds: India ✓, USA ✓
        #   - But the RELATIONSHIP is FALSE!
        # ------------------------------------------------------------------
        
        # ALWAYS query Google Fact Check if API key available
        # (This is the ONLY way to verify semantic meaning of claims)
        if self.google_api_key and self.google_api_calls_today < self.google_api_limit_daily:
            fact_checks = await self.google_factcheck(text, language)
            results["fact_checks"] = fact_checks
            results["google_verified"] = len(fact_checks) > 0
            
            if fact_checks:
                for fc in fact_checks[:3]:  # Top 3
                    results["sources"].append({
                        "name": fc.get("publisher", "Fact Checker"),
                        "url": fc.get("url", ""),
                        "verdict": fc.get("rating", ""),
                        "claim": fc.get("claim", "")
                    })
                
                # Adjust confidence based on fact check verdicts
                results["knowledge_confidence"] = self._calculate_knowledge_confidence(
                    fact_checks
                )
        else:
            if not self.google_api_key:
                logger.info("Google Fact Check API key not configured")
            elif self.google_api_calls_today >= self.google_api_limit_daily:
                logger.warning("Google Fact Check API daily quota exceeded")
            else:
                logger.info(f"Skipping Google API (confidence {confidence:.2f} >= 0.8)")
        
        return results
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities using spaCy multilingual NER
        
        Returns entities with labels like PERSON, ORG, GPE, DATE, etc.
        """
        # Lazy load NER model on first use
        if not self._nlp_loaded:
            self._nlp_loaded = True
            self.load_ner_model()
        
        if not self.nlp:
            logger.warning("NER model not available")
            return []
        
        try:
            doc = self.nlp(text[:1000])  # Limit to 1000 chars for performance
            entities = []
            
            for ent in doc.ents:
                # Filter for important entity types
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'LOC', 'FAC']:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char
                    })
            
            logger.info(f"Found {len(entities)} named entities")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def wikidata_lookup(self, entity_name: str, language: str = "en") -> Optional[Dict]:
        """
        Look up entity in Wikidata using SPARQL
        
        Free API, 5000 requests/hour limit (very generous)
        Tries multiple language codes for better multilingual support
        """
        try:
            # Escape quotes in entity name
            entity_name_escaped = entity_name.replace('"', '\\"')
            
            # Try multiple language codes for better coverage
            # 1. User's language
            # 2. English (most entities have English labels)
            # 3. Multilingual fallback
            languages_to_try = [language, "en"] if language != "en" else ["en"]
            
            for lang_code in languages_to_try:
                query = f'''
                SELECT ?item ?itemLabel ?itemDescription ?article WHERE {{
                  ?item rdfs:label "{entity_name_escaped}"@{lang_code} .
                  OPTIONAL {{ ?article schema:about ?item ; schema:isPartOf <https://{lang_code}.wikipedia.org/> . }}
                  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{lang_code},en" . }}
                }}
                LIMIT 1
                '''
                
                sparql = SPARQLWrapper(self.wikidata_endpoint)
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                sparql.setTimeout(5)
                
                # Execute query (synchronous)
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(None, sparql.query)
                data = results.convert()
                
                bindings = data.get("results", {}).get("bindings", [])
                
                if bindings:
                    item = bindings[0]
                    logger.info(f"Found Wikidata match for '{entity_name}' in language '{lang_code}'")
                    return {
                        "url": item.get("item", {}).get("value", ""),
                        "label": item.get("itemLabel", {}).get("value", ""),
                        "description": item.get("itemDescription", {}).get("value", "No description"),
                        "wikipedia": item.get("article", {}).get("value", "")
                    }
            
            logger.info(f"No Wikidata result for: {entity_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error querying Wikidata for '{entity_name}': {e}")
            return None
    
    # =========================================================================
    # RELATIONSHIP VERIFICATION (SNIFFER 2024 Enhancement)
    # Goes beyond entity existence to verify actual relationships
    # =========================================================================
    
    async def verify_capital_relationship(self, city: str, country: str, language: str = "en") -> Dict:
        """
        Verify if city is the capital of country using Wikidata P36 property
        
        Returns:
            {
                "verified": True/False/None,
                "confidence": float,
                "evidence": str,
                "sources": [...]
            }
        """
        logger.info(f"🔍 Verifying capital relationship: {city} ↔ {country}")
        
        try:
            # SPARQL query using P36 (capital) property
            query = f'''
            SELECT ?country ?countryLabel ?capital ?capitalLabel WHERE {{
                ?country wdt:P31 wd:Q6256 .     # Instance of country
                ?country wdt:P36 ?capital .     # Has capital
                ?country rdfs:label ?countryLabelRaw .
                ?capital rdfs:label ?capitalLabelRaw .
                FILTER(LANG(?countryLabelRaw) = "{language}" || LANG(?countryLabelRaw) = "en")
                FILTER(LANG(?capitalLabelRaw) = "{language}" || LANG(?capitalLabelRaw) = "en")
                FILTER(CONTAINS(LCASE(?countryLabelRaw), "{country.lower()}"))
                FILTER(CONTAINS(LCASE(?capitalLabelRaw), "{city.lower()}"))
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{language},en" . }}
            }}
            LIMIT 5
            '''
            
            sparql = SPARQLWrapper(self.wikidata_endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparql.setTimeout(10)
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, sparql.query)
            data = results.convert()
            
            bindings = data.get("results", {}).get("bindings", [])
            
            if bindings:
                # Found matching capital relationship
                result = bindings[0]
                country_label = result.get("countryLabel", {}).get("value", country)
                capital_label = result.get("capitalLabel", {}).get("value", city)
                
                logger.info(f"✅ Capital verification CONFIRMED: {capital_label} is capital of {country_label}")
                
                return {
                    "verified": True,
                    "confidence": 0.95,
                    "evidence": f"✅ **Verified by Wikidata**: {capital_label} is confirmed as the capital of {country_label}.",
                    "sources": [{
                        "name": "Wikidata Knowledge Graph",
                        "url": result.get("country", {}).get("value", "https://wikidata.org"),
                        "label": country_label
                    }]
                }
            else:
                # Capital relationship not found - try reverse check
                logger.info(f"❌ Capital relationship NOT found for: {city} → {country}")
                return {
                    "verified": None,  # Cannot determine
                    "confidence": 0.5,
                    "evidence": f"ℹ️ Could not verify capital relationship between {city} and {country}.",
                    "sources": []
                }
                
        except Exception as e:
            logger.error(f"Error verifying capital relationship: {e}")
            return {
                "verified": None,
                "confidence": 0.5,
                "evidence": "Verification service temporarily unavailable.",
                "sources": []
            }
    
    async def verify_location_relationship(self, place1: str, place2: str, language: str = "en") -> Dict:
        """
        Verify if place1 is located in place2 using Wikidata P131 property
        
        Returns similar structure to verify_capital_relationship
        """
        logger.info(f"🔍 Verifying location relationship: {place1} ↔ {place2}")
        
        try:
            query = f'''
            SELECT ?place1 ?place1Label ?place2 ?place2Label WHERE {{
                ?place1 wdt:P131+ ?place2 .     # Located in (transitive)
                ?place1 rdfs:label ?p1Label .
                ?place2 rdfs:label ?p2Label .
                FILTER(LANG(?p1Label) = "{language}" || LANG(?p1Label) = "en")
                FILTER(LANG(?p2Label) = "{language}" || LANG(?p2Label) = "en")
                FILTER(CONTAINS(LCASE(?p1Label), "{place1.lower()}"))
                FILTER(CONTAINS(LCASE(?p2Label), "{place2.lower()}"))
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{language},en" . }}
            }}
            LIMIT 5
            '''
            
            sparql = SPARQLWrapper(self.wikidata_endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparql.setTimeout(10)
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, sparql.query)
            data = results.convert()
            
            bindings = data.get("results", {}).get("bindings", [])
            
            if bindings:
                result = bindings[0]
                p1_label = result.get("place1Label", {}).get("value", place1)
                p2_label = result.get("place2Label", {}).get("value", place2)
                
                logger.info(f"✅ Location verification CONFIRMED: {p1_label} is in {p2_label}")
                
                return {
                    "verified": True,
                    "confidence": 0.92,
                    "evidence": f"✅ **Verified by Wikidata**: {p1_label} is located in {p2_label}.",
                    "sources": [{
                        "name": "Wikidata Knowledge Graph",
                        "url": "https://wikidata.org",
                        "label": p1_label
                    }]
                }
            else:
                return {
                    "verified": None,
                    "confidence": 0.5,
                    "evidence": f"ℹ️ Could not verify location relationship between {place1} and {place2}.",
                    "sources": []
                }
                
        except Exception as e:
            logger.error(f"Error verifying location relationship: {e}")
            return {"verified": None, "confidence": 0.5, "evidence": "Verification error.", "sources": []}
    
    async def verify_with_wikipedia(self, claim: str, language: str = "en") -> Dict:
        """
        Verify claim using Wikipedia REST API
        
        Useful for scientific facts and general knowledge verification
        """
        logger.info(f"📚 Verifying with Wikipedia: {claim[:50]}...")
        
        try:
            # Use Wikipedia REST API for fact verification
            wiki_api = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/"
            
            # Extract key terms from claim
            key_terms = claim.split()[:3]  # First 3 words as search
            search_term = "_".join(key_terms)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{wiki_api}{search_term}",
                    headers={"User-Agent": "FactWeave/1.0"}
                )
            
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                
                if extract:
                    return {
                        "verified": None,  # Wikipedia provides context, not verdict
                        "confidence": 0.6,
                        "evidence": f"📚 **Wikipedia Context**: {extract[:300]}...",
                        "sources": [{
                            "name": "Wikipedia",
                            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            "label": data.get("title", "")
                        }]
                    }
            
            return {
                "verified": None,
                "confidence": 0.5,
                "evidence": "No Wikipedia article found for this topic.",
                "sources": []
            }
            
        except Exception as e:
            logger.error(f"Error querying Wikipedia: {e}")
            return {"verified": None, "confidence": 0.5, "evidence": "Wikipedia unavailable.", "sources": []}
    
    async def google_factcheck(self, query: str, language: str = "en") -> List[Dict]:
        """
        Query Google Fact Check Tools API
        
        Rate limit: 1000 requests/day (FREE tier)
        Returns fact-check verdicts from 100+ organizations
        """
        if not self.google_api_key:
            logger.warning("Google Fact Check API key not provided")
            return []
        
        try:
            params = {
                "query": query[:500],  # Limit query length
                "key": self.google_api_key,
                "languageCode": language
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.google_factcheck_endpoint,
                    params=params
                )
            
            # Increment quota counter
            self.google_api_calls_today += 1
            logger.info(f"Google API calls today: {self.google_api_calls_today}/{self.google_api_limit_daily}")
            
            if response.status_code == 200:
                data = response.json()
                claims = data.get("claims", [])
                
                if not claims:
                    logger.info(f"No fact-checks found for query: {query[:50]}...")
                    return []
                
                fact_checks = []
                for claim in claims[:3]:  # Top 3 most relevant
                    claim_reviews = claim.get("claimReview", [])
                    for review in claim_reviews[:2]:  # Top 2 reviews per claim
                        fact_checks.append({
                            "publisher": review.get("publisher", {}).get("name", "Unknown"),
                            "url": review.get("url", ""),
                            "rating": review.get("textualRating", "Unrated"),
                            "claim": claim.get("text", ""),
                            "claimant": claim.get("claimant", "Unknown")
                        })
                
                logger.info(f"Found {len(fact_checks)} fact-checks")
                return fact_checks
            
            elif response.status_code == 429:
                logger.warning("Google Fact Check API rate limit exceeded")
                return []
            elif response.status_code == 403:
                logger.error("Google Fact Check API key invalid or unauthorized")
                return []
            else:
                logger.warning(f"Google API returned status {response.status_code}")
                return []
            
        except httpx.TimeoutException:
            logger.error("Google Fact Check API timeout")
            return []
        except Exception as e:
            logger.error(f"Error querying Google Fact Check: {e}")
            return []
    
    def _calculate_knowledge_confidence(self, fact_checks: List[Dict]) -> float:
        """
        Calculate confidence based on fact-check verdicts
        
        Maps textual ratings to confidence scores:
        - False/Fake -> 0.9 (high confidence it's misinformation)
        - True/Correct -> 0.1 (high confidence it's authentic)
        - Mixed/Partially -> 0.5 (uncertain)
        """
        if not fact_checks:
            return 0.5
        
        ratings_lower = [fc.get("rating", "").lower() for fc in fact_checks]
        
        # Count verdicts
        false_count = sum(
            1 for r in ratings_lower 
            if any(word in r for word in ['false', 'fake', 'incorrect', 'misleading'])
        )
        true_count = sum(
            1 for r in ratings_lower 
            if any(word in r for word in ['true', 'correct', 'accurate'])
        )
        
        total = len(fact_checks)
        
        if false_count > true_count:
            # More false ratings -> high confidence misinformation
            return 0.7 + (false_count / total) * 0.25  # 0.7 to 0.95
        elif true_count > false_count:
            # More true ratings -> high confidence authentic
            return 0.3 - (true_count / total) * 0.25  # 0.05 to 0.3
        else:
            # Mixed or uncertain
            return 0.5
    
    def _check_and_reset_quota(self):
        """Reset daily quota counter if a new day has started"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.google_api_calls_today = 0
            self.last_reset = now
            logger.info("Daily quota reset for Google Fact Check API")
    
    async def claimbuster_check_worthiness(self, text: str) -> float:
        """
        Check claim worthiness using ClaimBuster API
        
        Returns score 0-1 (higher = more check-worthy)
        Free API, no quota limits
        """
        if not hasattr(self, 'claimbuster_key') or not self.claimbuster_key:
            logger.info("ClaimBuster API key not configured")
            return 0.5  # Default: assume moderately check-worthy
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://idir.uta.edu/claimbuster/api/v2/score/text/",
                    json={
                        "input_text": text[:500],  # Limit to 500 chars
                        "api_key": self.claimbuster_key
                    }
                )
            
            if response.status_code == 200:
                data = response.json()
                score = data.get("score", 0.5)
                logger.info(f"ClaimBuster check-worthiness: {score:.2f}")
                return float(score)
            else:
                logger.warning(f"ClaimBuster API returned status {response.status_code}")
                return 0.5
                
        except httpx.TimeoutException:
            logger.error("ClaimBuster API timeout")
            return 0.5
        except Exception as e:
            logger.error(f"Error calling ClaimBuster: {e}")
            return 0.5


# Global instance (will be initialized with API key from settings)
knowledge_verifier: Optional[KnowledgeGraphVerifier] = None


def initialize_knowledge_verifier(google_api_key: Optional[str] = None, claimbuster_key: Optional[str] = None):
    """Initialize the global knowledge verifier instance"""
    global knowledge_verifier
    
    verifier = KnowledgeGraphVerifier(google_api_key=google_api_key)
    
    # Add ClaimBuster key if provided
    if claimbuster_key:
        verifier.claimbuster_key = claimbuster_key
        logger.info("✅ Knowledge graph verifier initialized with ClaimBuster API key")
    
    knowledge_verifier = verifier
    
    if google_api_key:
        logger.info("✅ Knowledge graph verifier initialized with Google API key")
    else:
        logger.warning("⚠️ Knowledge graph verifier initialized without Google API key")
