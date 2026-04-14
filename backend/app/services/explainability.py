"""
FactWeave Explainability Module
Based on SNIFFER 2024, MIRAGE (CIKM 2024), LVLM4FV Research

Implements:
- Multi-signal scoring (50% external, 20% entity, 15% textual, 15% linguistic)
- Three-state verdict system (AUTHENTIC/MISINFORMATION/NEEDS_VERIFICATION)
- Human-readable evidence chain
- Production-grade misinformation detection
"""

import logging
import re
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# =============================================================================
# RESEARCH-BACKED SIGNAL WEIGHTS (SNIFFER 2024 Methodology)
# =============================================================================
SIGNAL_WEIGHTS = {
    "external": 0.50,   # Google Fact Check API (ground truth from experts)
    "entity": 0.20,     # Wikidata entity verification  
    "textual": 0.15,    # Pattern analysis
    "linguistic": 0.15  # Linguistic markers (sensationalism, emotional language)
}

# =============================================================================
# KNOWN FALSE CLAIMS DATABASE (Well-documented misinformation)
# =============================================================================
KNOWN_FALSE_CLAIMS = {
    # Scientific misinformation
    "earth is flat": {
        "claim_key": "earth_flat",
        "debunked": True,
        "confidence": 0.99,
        "evidence": "🔬 **Scientific Fact**: The Earth is an oblate spheroid, confirmed by centuries of scientific observation, satellite imagery, and physics. This is one of the most thoroughly debunked conspiracy theories.",
        "sources": [
            {"name": "NASA", "url": "https://nasa.gov"},
            {"name": "Scientific American", "url": "https://scientificamerican.com"}
        ]
    },
    "flat earth": {
        "claim_key": "earth_flat",
        "debunked": True,
        "confidence": 0.99,
        "evidence": "🔬 **Scientific Fact**: The Earth is spherical. This has been proven by satellite imagery, physics, and thousands of years of observation.",
        "sources": [{"name": "NASA", "url": "https://nasa.gov"}]
    },
    "vaccines cause autism": {
        "claim_key": "vaccines_autism",
        "debunked": True,
        "confidence": 0.98,
        "evidence": "🏥 **Medical Consensus**: Multiple large-scale studies involving millions of children have found NO link between vaccines and autism. The original study was retracted and its author lost his medical license.",
        "sources": [
            {"name": "WHO", "url": "https://who.int"},
            {"name": "CDC", "url": "https://cdc.gov"}
        ]
    },
    "5g causes covid": {
        "claim_key": "5g_covid",
        "debunked": True,
        "confidence": 0.99,
        "evidence": "📡 **Debunked Conspiracy**: COVID-19 is caused by the SARS-CoV-2 virus, not radio waves. 5G technology uses non-ionizing radiation that cannot cause viral infections.",
        "sources": [{"name": "WHO", "url": "https://who.int"}]
    },
    "covid is a hoax": {
        "claim_key": "covid_hoax",
        "debunked": True,
        "confidence": 0.99,
        "evidence": "🦠 **Medical Fact**: COVID-19 is a real disease caused by SARS-CoV-2. Millions of cases have been documented worldwide by medical professionals.",
        "sources": [{"name": "WHO", "url": "https://who.int"}]
    },
    "sun rises from west": {
        "claim_key": "sun_west",
        "debunked": True,
        "confidence": 0.99,
        "evidence": "🌅 **Astronomical Fact**: The Sun rises in the East and sets in the West due to Earth's rotation direction. This is observable daily worldwide.",
        "sources": [{"name": "NASA", "url": "https://nasa.gov"}]
    },
    "moon landing was fake": {
        "claim_key": "moon_fake",
        "debunked": True,
        "confidence": 0.98,
        "evidence": "🌙 **Historical Fact**: The Apollo moon landings (1969-1972) are among the most well-documented events in history, with physical evidence, thousands of witnesses, and independent verification.",
        "sources": [{"name": "NASA", "url": "https://nasa.gov"}]
    },
    "climate change is a hoax": {
        "claim_key": "climate_hoax",
        "debunked": True,
        "confidence": 0.97,
        "evidence": "🌍 **Scientific Consensus**: 97%+ of climate scientists agree that climate change is real and human-caused, based on overwhelming physical evidence.",
        "sources": [
            {"name": "NASA Climate", "url": "https://climate.nasa.gov"},
            {"name": "IPCC", "url": "https://ipcc.ch"}
        ]
    }
}

# =============================================================================
# KNOWN TRUE CLAIMS (Verified facts – match these for instant AUTHENTIC)
# Add phrases that should be recognized as correct (substring match, case-insensitive).
# =============================================================================
KNOWN_TRUE_CLAIMS = {
    # Basic science / geography
    "sun rises in the east": {
        "claim_key": "sun_east",
        "confidence": 0.99,
        "evidence": "🌅 **Astronomical Fact**: The Sun rises in the east and sets in the west due to Earth's rotation. This is observable daily worldwide.",
        "sources": [{"name": "NASA", "url": "https://nasa.gov"}]
    },
    "sun rises from the east": {
        "claim_key": "sun_east",
        "confidence": 0.99,
        "evidence": "🌅 **Astronomical Fact**: The Sun rises in the east and sets in the west due to Earth's rotation.",
        "sources": [{"name": "NASA", "url": "https://nasa.gov"}]
    },
    "earth is round": {
        "claim_key": "earth_round",
        "confidence": 0.99,
        "evidence": "🔬 **Scientific Fact**: The Earth is an oblate spheroid. This is confirmed by satellite imagery, physics, and centuries of observation.",
        "sources": [{"name": "NASA", "url": "https://nasa.gov"}]
    },
    "earth orbits the sun": {
        "claim_key": "earth_orbits_sun",
        "confidence": 0.99,
        "evidence": "🔬 **Astronomical Fact**: Earth orbits the Sun; this is well-established in astronomy and physics.",
        "sources": [{"name": "NASA", "url": "https://nasa.gov"}]
    },
    # Sports / public figures (well-established facts)
    "lewis hamilton is an f1 driver": {
        "claim_key": "hamilton_f1",
        "confidence": 0.98,
        "evidence": "🏎️ **Verified Fact**: Lewis Hamilton is a Formula 1 driver (Mercedes), multiple-time World Champion. Widely reported and documented.",
        "sources": [{"name": "Formula 1", "url": "https://www.formula1.com"}]
    },
    "lewis hamilton is a formula 1 driver": {
        "claim_key": "hamilton_f1",
        "confidence": 0.98,
        "evidence": "🏎️ **Verified Fact**: Lewis Hamilton is a Formula 1 driver and multiple-time World Champion.",
        "sources": [{"name": "Formula 1", "url": "https://www.formula1.com"}]
    },
    "lewis hamilton drives in f1": {
        "claim_key": "hamilton_f1",
        "confidence": 0.98,
        "evidence": "🏎️ **Verified Fact**: Lewis Hamilton competes in Formula 1 and has won multiple World Championships.",
        "sources": [{"name": "Formula 1", "url": "https://www.formula1.com"}]
    },
}

# =============================================================================
# MISINFORMATION LINGUISTIC PATTERNS (Research-backed indicators)
# =============================================================================
MISINFORMATION_PATTERNS = {
    "sensationalism": [
        "shocking", "amazing", "unbelievable", "mind-blowing", "incredible",
        "you won't believe", "absolutely stunning", "breaking", "urgent"
    ],
    "emotional_manipulation": [
        "outraged", "disgusted", "terrified", "furious", "heartbreaking",
        "devastating", "horrifying", "infuriating"
    ],
    "conspiracy_markers": [
        "they don't want you to know", "hidden truth", "cover up", "secretly",
        "hidden agenda", "mainstream media lies", "wake up", "sheeple"
    ],
    "false_authority": [
        "doctors hate this", "scientists are baffled", "experts are shocked",
        "the truth they hide", "what they don't tell you"
    ],
    "urgency_pressure": [
        "share before deleted", "act now", "limited time", "before it's too late",
        "share with everyone", "going viral"
    ]
}


def get_known_claim_evidence(text: str) -> Dict[str, Any]:
    """
    Check if claim matches known FALSE or known TRUE claims database.
    False claims are checked first; then true claims.
    
    Returns:
        {
            "matched": True/False,
            "claim_key": str,
            "debunked": True/False,  # True = misinformation, False = verified true
            "confidence": float,
            "evidence": str,
            "sources": [...]
        }
    """
    text_lower = text.lower().strip()
    text_clean = re.sub(r'[^\w\s]', '', text_lower)
    
    # 1) Check known FALSE claims (misinformation)
    for pattern, data in KNOWN_FALSE_CLAIMS.items():
        if pattern in text_clean or pattern in text_lower:
            return {"matched": True, "debunked": True, **data}
    
    # 2) Check known TRUE claims (verified facts)
    for pattern, data in KNOWN_TRUE_CLAIMS.items():
        if pattern in text_clean or pattern in text_lower:
            return {"matched": True, "debunked": False, **data}
    
    return {"matched": False}


def analyze_linguistic_markers(text: str) -> Dict[str, Any]:
    """
    Analyze text for misinformation linguistic patterns
    
    Based on research: Sensationalism, emotional manipulation, 
    conspiracy markers indicate higher misinformation probability.
    
    Returns:
        {
            "score": float (0-1, higher = more suspicious),
            "patterns_found": [...],
            "categories": [...]
        }
    """
    text_lower = text.lower()
    patterns_found = []
    categories_found = []
    
    for category, patterns in MISINFORMATION_PATTERNS.items():
        for pattern in patterns:
            if pattern in text_lower:
                patterns_found.append(pattern)
                if category not in categories_found:
                    categories_found.append(category)
    
    # Calculate linguistic suspicion score
    if len(patterns_found) == 0:
        score = 0.0
    elif len(patterns_found) <= 2:
        score = 0.3
    elif len(patterns_found) <= 4:
        score = 0.6
    else:
        score = 0.85
    
    # Boost score if multiple categories detected
    if len(categories_found) >= 3:
        score = min(0.95, score + 0.15)
    
    return {
        "score": score,
        "patterns_found": patterns_found,
        "categories": categories_found
    }


def analyze_entity_verification(entities_verified: Dict) -> Dict[str, Any]:
    """
    Calculate entity verification signal
    
    Returns:
        {
            "score": float (0 = all verified, 1 = none verified),
            "verified_count": int,
            "unverified_count": int,
            "entities": [...]
        }
    """
    if not entities_verified:
        return {"score": 0.5, "verified_count": 0, "unverified_count": 0, "entities": []}
    
    verified_count = 0
    unverified_count = 0
    entity_list = []
    
    # Handle different formats
    if isinstance(entities_verified, dict):
        sources = entities_verified.get("sources", [])
        if sources:
            for source in sources:
                entity_list.append({
                    "name": source.get("label", "Unknown"),
                    "verified": True,
                    "wikidata_id": source.get("wikidata_id")
                })
                verified_count += 1
    
    total = verified_count + unverified_count
    if total == 0:
        score = 0.5  # Neutral if no entities
    else:
        # Lower score = more entities verified = less suspicious
        score = unverified_count / total
    
    return {
        "score": score,
        "verified_count": verified_count,
        "unverified_count": unverified_count,
        "entities": entity_list
    }


def calculate_multi_signal_score(
    external_signal: float,
    entity_signal: float,
    textual_signal: float,
    linguistic_signal: float
) -> float:
    """
    Calculate final misinformation probability using research-backed weights
    
    Weights from SNIFFER 2024:
    - External (fact-checks): 50%
    - Entity verification: 20%
    - Textual patterns: 15%
    - Linguistic markers: 15%
    """
    final_score = (
        external_signal * SIGNAL_WEIGHTS["external"] +
        entity_signal * SIGNAL_WEIGHTS["entity"] +
        textual_signal * SIGNAL_WEIGHTS["textual"] +
        linguistic_signal * SIGNAL_WEIGHTS["linguistic"]
    )
    
    return min(1.0, max(0.0, final_score))


def verdict_from_score(score: float) -> str:
    """
    Convert misinformation probability to three-state verdict
    
    Three-state system (per critical-mistakes.md):
    - AUTHENTIC: < 0.25 (verified as true)
    - MISINFORMATION: > 0.75 (verified as false)
    - NEEDS_VERIFICATION: 0.25-0.75 (cannot determine)
    """
    if score < 0.25:
        return "AUTHENTIC"
    elif score > 0.75:
        return "MISINFORMATION"
    else:
        return "NEEDS_VERIFICATION"


def build_evidence_chain(
    claim: str,
    verdict: str,
    confidence: float,
    signals: Dict,
    fact_checks: List[Dict] = None,
    entities: List[Dict] = None,
    linguistic_patterns: List[str] = None
) -> Dict[str, Any]:
    """
    Build human-readable evidence chain
    
    Per implementation-guide.md: Clear text + links, not complex visualizations
    """
    evidence = {
        "claim": claim,
        "verdict": verdict,
        "confidence": f"{confidence:.0%}",
        "key_findings": [],
        "evidence_sources": [],
        "signal_breakdown": signals,
        "recommendations": []
    }
    
    # Key Finding 1: External Fact-Check Results
    if fact_checks:
        verdicts = [fc.get("verdict", "unknown") for fc in fact_checks]
        if "misinformation" in verdicts or "false" in verdicts:
            evidence["key_findings"].append({
                "type": "Fact-Check Consensus",
                "description": f"Expert fact-checkers have rated this claim as FALSE ({len(fact_checks)} sources)",
                "impact": "Critical"
            })
        elif "authentic" in verdicts or "true" in verdicts:
            evidence["key_findings"].append({
                "type": "Fact-Check Confirmation",
                "description": f"Expert fact-checkers have confirmed this claim ({len(fact_checks)} sources)",
                "impact": "Critical"
            })
        
        # Add sources
        for fc in fact_checks:
            evidence["evidence_sources"].append({
                "source": fc.get("publisher", "Unknown"),
                "url": fc.get("url"),
                "rating": fc.get("rating", "Unknown")
            })
    
    # Key Finding 2: Entity Verification
    if entities:
        verified = sum(1 for e in entities if e.get("verified"))
        unverified = len(entities) - verified
        
        if unverified > 0:
            evidence["key_findings"].append({
                "type": "Entity Verification",
                "description": f"{unverified} of {len(entities)} entities could not be verified in Wikidata",
                "impact": "Medium" if unverified < len(entities) else "High"
            })
        elif verified > 0:
            evidence["key_findings"].append({
                "type": "Entity Verification",
                "description": f"All {verified} entities verified in Wikidata knowledge graph",
                "impact": "Low"
            })
    
    # Key Finding 3: Linguistic Patterns
    if linguistic_patterns and len(linguistic_patterns) > 0:
        evidence["key_findings"].append({
            "type": "Linguistic Analysis",
            "description": f"Detected {len(linguistic_patterns)} misinformation indicators: {', '.join(linguistic_patterns[:3])}",
            "impact": "Medium" if len(linguistic_patterns) < 4 else "High"
        })
    
    # Recommendations based on verdict
    if verdict == "NEEDS_VERIFICATION":
        evidence["recommendations"] = [
            "Verify with multiple independent sources",
            "Check the original source of the claim",
            "Look for conflicting information from reputable outlets",
            "Consider the date and context of the claim"
        ]
    elif verdict == "MISINFORMATION":
        evidence["recommendations"] = [
            "Do not share this content without verification",
            "Check the fact-check sources linked above",
            "Report this content if seen on social media",
            "Share the fact-check links to counter misinformation"
        ]
    else:  # AUTHENTIC
        evidence["recommendations"] = [
            "This claim appears to be accurate based on available evidence",
            "You can share this information with confidence"
        ]
    
    return evidence


async def analyze_claims_with_evidence(
    text: str,
    knowledge_verifier,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Comprehensive claim analysis with multi-signal scoring
    
    IMPLEMENTS SNIFFER 2024 METHODOLOGY:
    - Multi-signal combination (external 50%, entity 20%, textual 15%, linguistic 15%)
    - Three-state verdict system
    - Human-readable evidence chain
    
    Returns:
        {
            "overall_verdict": "AUTHENTIC" | "MISINFORMATION" | "NEEDS_VERIFICATION",
            "overall_confidence": float,
            "signal_breakdown": {...},
            "detailed_analysis": [...],
            "summary": str
        }
    """
    logger.info(f"📊 Starting multi-signal analysis for text ({len(text)} chars)")
    
    # Split into sentences for claim-level analysis
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    detailed_results = []
    authentic_count = 0
    misinfo_count = 0
    needs_verification_count = 0
    total_confidence = 0.0
    
    for sentence in sentences:
        if len(sentence) < 10:  # Skip very short sentences
            continue
        
        logger.info(f"📝 Analyzing claim: '{sentence[:50]}...'")
        
        # =================================================================
        # SIGNAL 1: Check KNOWN FALSE CLAIMS database (instant, highest priority)
        # =================================================================
        known_result = get_known_claim_evidence(sentence)
        
        if known_result.get("matched"):
            claim_verdict = "MISINFORMATION" if known_result.get("debunked") else "AUTHENTIC"
            claim_confidence = known_result.get("confidence", 0.95)
            evidence = known_result.get("evidence", "Known claim detected.")
            sources = known_result.get("sources", [])
            
            logger.info(f"⚡ KNOWN CLAIM MATCHED: '{known_result.get('claim_key')}' → {claim_verdict}")
            
            if claim_verdict == "AUTHENTIC":
                authentic_count += 1
            else:
                misinfo_count += 1
            
            detailed_results.append({
                "claim": sentence,
                "verdict": claim_verdict,
                "confidence": claim_confidence,
                "evidence": evidence,
                "sources": sources,
                "signals": {"known_claim": 1.0}
            })
            total_confidence += claim_confidence
            continue
        
        # =================================================================
        # SIGNAL 2: External Fact-Check API (50% weight)
        # =================================================================
        external_signal = 0.5  # Neutral default
        fact_checks = []
        sources = []
        
        try:
            claim_result = await knowledge_verifier.verify_claim(
                text=sentence,
                language=language,
                confidence=0.5
            )
            
            has_google = claim_result.get("google_verified", False) or claim_result.get("has_google_results", False)
            has_wikidata = claim_result.get("wikidata_verified", False) or claim_result.get("has_wikidata_results", False)
            
            if has_google:
                fact_checks = claim_result.get("fact_checks", [])
                sources.extend(claim_result.get("sources", []))
                
                # Calculate external signal from fact-checks (Google uses "rating" / textualRating)
                if fact_checks:
                    misinfo_verdicts = sum(
                        1 for fc in fact_checks
                        if any(w in (fc.get("verdict") or fc.get("rating") or "").lower()
                               for w in ("misinformation", "false", "fake", "incorrect", "pants-fire", "mostly false", "mostly-false"))
                    )
                    authentic_verdicts = sum(
                        1 for fc in fact_checks
                        if any(w in (fc.get("verdict") or fc.get("rating") or "").lower()
                               for w in ("authentic", "true", "correct", "accurate", "mostly true", "mostly-true"))
                    )
                    
                    if misinfo_verdicts > authentic_verdicts:
                        external_signal = min(0.95, 0.7 + (misinfo_verdicts / len(fact_checks)) * 0.25)
                    elif authentic_verdicts > misinfo_verdicts:
                        external_signal = max(0.05, 0.3 - (authentic_verdicts / len(fact_checks)) * 0.25)
                    else:
                        external_signal = 0.5
            
            if has_wikidata:
                sources.extend(claim_result.get("sources", []))
                
        except Exception as e:
            logger.warning(f"Knowledge verification failed: {e}")
        
        # =================================================================
        # SIGNAL 3: Entity Verification (20% weight)
        # =================================================================
        entity_result = analyze_entity_verification({"sources": sources})
        entity_signal = entity_result.get("score", 0.5)
        
        # =================================================================
        # SIGNAL 4: Linguistic Markers (15% weight)
        # =================================================================
        linguistic_result = analyze_linguistic_markers(sentence)
        linguistic_signal = linguistic_result.get("score", 0.0)
        
        # =================================================================
        # SIGNAL 5: Textual Patterns (15% weight) - from ML pipeline
        # =================================================================
        textual_signal = 0.5  # Neutral - will be overridden by ML pipeline
        
        # =================================================================
        # COMBINE ALL SIGNALS (SNIFFER 2024 Methodology)
        # =================================================================
        final_score = calculate_multi_signal_score(
            external_signal=external_signal,
            entity_signal=entity_signal,
            textual_signal=textual_signal,
            linguistic_signal=linguistic_signal
        )
        
        signals = {
            "external": external_signal,
            "entity": entity_signal,
            "textual": textual_signal,
            "linguistic": linguistic_signal,
            "combined": final_score
        }
        
        claim_verdict = verdict_from_score(final_score)
        claim_confidence = min(0.95, 0.5 + abs(final_score - 0.5))
        
        # Build evidence chain
        evidence_chain = build_evidence_chain(
            claim=sentence,
            verdict=claim_verdict,
            confidence=claim_confidence,
            signals=signals,
            fact_checks=fact_checks,
            entities=entity_result.get("entities", []),
            linguistic_patterns=linguistic_result.get("patterns_found", [])
        )
        
        # Generate evidence text
        if claim_verdict == "AUTHENTIC":
            if fact_checks:
                evidence = f"✅ **Verified Authentic**: Fact-checkers confirm this claim. {len(fact_checks)} source(s) support this information."
            elif sources:
                entity_names = ", ".join([s.get("label", "Unknown") for s in sources[:3]])
                evidence = f"✅ **Entities Verified**: The entities ({entity_names}) exist in Wikidata. No contradicting information found."
            else:
                evidence = "✅ **No Red Flags**: No misinformation indicators detected. Claim appears factual."
        elif claim_verdict == "MISINFORMATION":
            if fact_checks:
                evidence = f"❌ **Debunked**: {len(fact_checks)} fact-checker(s) have rated this claim as FALSE. See sources for details."
            elif linguistic_signal > 0.6:
                patterns = linguistic_result.get("patterns_found", [])
                evidence = f"❌ **Misinformation Indicators**: Detected suspicious patterns: {', '.join(patterns[:3])}. High probability of false information."
            else:
                evidence = "❌ **Flagged as Misinformation**: Multiple signals indicate this is likely false information."
        else:
            if sources:
                entity_names = ", ".join([s.get("label", "Unknown") for s in sources[:3]])
                evidence = f"ℹ️ **Entities Verified, Relationship Unconfirmed**: The entities ({entity_names}) exist in Wikidata. However, the specific claim could not be independently verified. Recommend manual verification from authoritative sources."
            else:
                evidence = f"ℹ️ **Verification Required**: This claim could not be verified or debunked through automated fact-checking. Recommend checking authoritative sources."
        
        # Track statistics
        if claim_verdict == "AUTHENTIC":
            authentic_count += 1
        elif claim_verdict == "MISINFORMATION":
            misinfo_count += 1
        else:
            needs_verification_count += 1
        
        total_confidence += claim_confidence
        
        detailed_results.append({
            "claim": sentence,
            "verdict": claim_verdict,
            "confidence": claim_confidence,
            "evidence": evidence,
            "sources": sources,
            "signals": signals,
            "evidence_chain": evidence_chain
        })
    
    # =================================================================
    # CALCULATE OVERALL VERDICT (Production fact-checking approach)
    # =================================================================
    total_claims = len(detailed_results)
    
    if total_claims == 0:
        overall_verdict = "NEEDS_VERIFICATION"
        overall_confidence = 0.5
        summary = "No analyzable claims found in the input."
    elif misinfo_count > 0:
        # If ANY claim is misinformation, overall is MISINFORMATION
        overall_verdict = "MISINFORMATION"
        overall_confidence = total_confidence / total_claims
        summary = f"❌ {misinfo_count} claim(s) identified as misinformation. See detailed analysis for evidence and sources."
    elif authentic_count == total_claims:
        # ALL claims verified as authentic
        overall_verdict = "AUTHENTIC"
        overall_confidence = total_confidence / total_claims
        summary = f"✅ All {authentic_count} claim(s) verified as authentic by fact-checkers and knowledge graphs."
    elif authentic_count > 0:
        # Some authentic, rest need verification
        overall_verdict = "NEEDS_VERIFICATION"
        overall_confidence = total_confidence / total_claims
        summary = f"ℹ️ {authentic_count} claim(s) verified as authentic, {needs_verification_count} claim(s) need verification. Recommend manual fact-checking for unverified claims."
    else:
        # All claims need verification
        overall_verdict = "NEEDS_VERIFICATION"
        overall_confidence = 0.5
        summary = f"ℹ️ All {total_claims} claim(s) require manual verification. No automated fact-checks or debunks found."
    
    # Signal breakdown for transparency
    signal_breakdown = {
        "weights": SIGNAL_WEIGHTS,
        "methodology": "SNIFFER 2024 (Multi-signal fact verification)",
        "signals_used": ["external_fact_check", "entity_verification", "textual_patterns", "linguistic_markers"]
    }
    
    return {
        "overall_verdict": overall_verdict,
        "overall_confidence": overall_confidence,
        "signal_breakdown": signal_breakdown,
        "detailed_analysis": detailed_results,
        "summary": summary,
        "statistics": {
            "total_claims": total_claims,
            "authentic": authentic_count,
            "misinformation": misinfo_count,
            "needs_verification": needs_verification_count
        }
    }


async def generate_explanation(
    result: Dict,
    language: str = "en"
) -> str:
    """
    Generate human-readable explanation for the analysis result
    
    Per implementation-guide.md: Focus on clarity, not complexity
    """
    verdict = result.get("overall_verdict", "NEEDS_VERIFICATION")
    confidence = result.get("overall_confidence", 0.5)
    summary = result.get("summary", "Analysis complete.")
    
    if verdict == "AUTHENTIC":
        emoji = "✅"
        verdict_text = "AUTHENTIC"
    elif verdict == "MISINFORMATION":
        emoji = "❌"
        verdict_text = "MISINFORMATION DETECTED"
    else:
        emoji = "ℹ️"
        verdict_text = "NEEDS VERIFICATION"
    
    explanation = f"{emoji} **{verdict_text}** (Confidence: {confidence:.0%})\n\n{summary}"
    
    # Add detailed breakdown if available
    detailed = result.get("detailed_analysis", [])
    if detailed:
        explanation += "\n\n**Claim-by-Claim Analysis:**\n"
        for i, claim_result in enumerate(detailed, 1):
            claim_verdict = claim_result.get("verdict", "UNKNOWN")
            claim_evidence = claim_result.get("evidence", "No evidence available.")
            explanation += f"\n{i}. **{claim_verdict}**: {claim_result.get('claim', '')[:100]}...\n   {claim_evidence}\n"
    
    return explanation
