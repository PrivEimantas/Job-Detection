import google.generativeai as genai
import json,os


api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=api_key)

class JuniorChecker:
    def __init__(self):
        self.driver = None

        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        # self.client = genai.Client()



    def check_if_junior(self,json_data):
        """
        Analyzes a job posting to determine if it's truly a junior role.
        Returns a score from 0-10 where 8+ indicates high confidence it's junior.
        """

        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""Analyze this job posting and determine if it's truly a JUNIOR-level position.

        Job Data:
        {json.dumps(json_data, indent=2)}
    
        Consider these factors:
        1. Job title (does it say "Junior", "Graduate", "Entry-level", or similar?)
        2. Required years of experience (0-2 years = junior, 3+ = not junior)
        3. Salary range (UK context: £18k-£35k typically junior, £35k-£50k mid, £50k+ senior)
        4. Technical skills complexity (basic frameworks vs advanced architecture)
        5. Job responsibilities (learning/support vs leading/architecting)
        6. Seniority indicators in description (words like "lead", "mentor", "architect", "senior responsibilities")
    
        Score from 0-10 where:
        - 0-3: Definitely not junior (senior/lead level)
        - 4-5: Mid-level position
        - 6-7: Could be junior+ or borderline
        - 8-10: Clearly junior/entry-level
    
        Return ONLY a JSON object in this exact format:
        {{
          "junior_score": <number 0-10>,
          "is_junior": <true if score >= 8, false otherwise>,
          "confidence_level": "<low/medium/high>",
          "reasoning": "<brief explanation>",
          "red_flags": [<list of non-junior indicators>],
          "junior_indicators": [<list of junior indicators>]
        }}"""

        response = model.generate_content(prompt)

        # Parse the response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].split('```')[0].strip()

        result = json.loads(response_text)
        return result


if __name__ == "__main__":
    job_posting = {
        "title": "Full Stack Developer",
        "company": "true",
        "location": "51 Frederick Road, Salford M6 6FP",
        "salary": "£60,000 - £70,000 a year",
        "job_type": "Full-time",
        "benefits": [
            "Life insurance",
            "Free parking",
            "Company pension",
            "Private medical insurance",
            "On-site parking"
        ],
        "description": "We are looking for an experienced Full Stack Developer to join our team. You will be responsible for developing and maintaining web applications using modern technologies.",
        "url": "https://example.com/job"
    }

    checker = JuniorChecker()

    result = checker.check_if_junior(job_posting)

    print(f"Junior Score: {result['junior_score']}/10")
    print(f"Is Junior: {result['is_junior']}")
    print(f"Confidence: {result['confidence_level']}")
    print(f"\nReasoning: {result['reasoning']}")

    if result['red_flags']:
        print(f"\nRed Flags (Non-Junior Indicators):")
        for flag in result['red_flags']:
            print(f"  - {flag}")

    if result['junior_indicators']:
        print(f"\nJunior Indicators:")
        for indicator in result['junior_indicators']:
            print(f"  - {indicator}")


