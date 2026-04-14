import httpx

def fact_check(query):
    api_key = "AIzaSyBQaWEtDsrHopm82LQPtqblEcbO8Hwudeo"
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={api_key}"
    
    response = httpx.get(url)
    data = response.json()

    # Log the response
    print(data)

    if "claims" in data:
        return data["claims"]
    else:
        return "No fact-checks found."

# Example query for debugging
fact_check("lewis hamilton is a driver")