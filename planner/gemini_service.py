import os
import json
import logging
import warnings
# Suppress all FutureWarning alerts
warnings.filterwarnings("ignore", category=FutureWarning)
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)

def generate_project_analysis(idea_name, description, time_available, budget, skills, goal):
    """
    Calls the Gemini API to analyze a project idea and return structured planning data.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key or api_key == 'your_gemini_api_key_here':
        raise ValueError("Gemini API Key is not configured. Please set a valid GEMINI_API_KEY in the .env file.")

    genai.configure(api_key=api_key)
    
    # Use gemini-3.5-flash as the default model
    model = genai.GenerativeModel('gemini-3.5-flash')

    prompt = f"""
You are an expert startup advisor, venture strategist, and project management master.
Analyze the following user project idea and constraints, then output a structured analysis report in JSON format.

=== USER INPUTS ===
1. Idea Name: {idea_name}
2. Description: {description}
3. Time Available per Week: {time_available} hours
4. Budget: ${budget}
5. Existing Skills: {skills}
6. Goal/Outcome: {goal}

=== INSTRUCTIONS ===
Perform a detailed planning analysis based on these inputs. Your response must be a single, valid JSON object containing exactly the following structure.

JSON Structure:
{{
  "problem_statement": "A clear, concise definition of the problem being solved.",
  "target_audience": "Specific groups of people who face this problem and will use this solution.",
  "value_proposition": "The unique value this idea offers to solve the problem for the target audience.",
  "key_assumptions": [
    "Assumption 1: Core assumption about user behavior or need.",
    "Assumption 2: Technical or feasibility assumption.",
    "Assumption 3: Market or commercial assumption."
  ],
  "readiness_interpretation": "A professional Venture Strategist explanation explaining the readiness viability based on budget, skills, and weekly time.",
  "risk_level": 4,
  "confidence_score": 85,
  "confidence_reasoning": "A summary explaining the reasoning behind the confidence percentage score.",
  "assumptions": [
    {{
      "category": "User",
      "assumption": "User behavior assumption (e.g. users will upload files).",
      "risk": "Medium",
      "explanation": "Explanation of why this assumption holds risk.",
      "validation_recommendation": "Validation Step (e.g. Conduct a survey)."
    }},
    {{
      "category": "Market",
      "assumption": "Market demand assumption.",
      "risk": "High",
      "explanation": "Explanation of potential market risks.",
      "validation_recommendation": "Validation Step (e.g. Build a landing page)."
    }},
    {{
      "category": "Technical",
      "assumption": "Technical requirement assumption.",
      "risk": "Low",
      "explanation": "Explanation of complexity.",
      "validation_recommendation": "Validation Step."
    }},
    {{
      "category": "Resource",
      "assumption": "Resource availability assumption.",
      "risk": "Medium",
      "explanation": "Explanation of cost/time risks.",
      "validation_recommendation": "Validation Step."
    }}
  ],
  "feasibility": {{
    "time_score": 8,
    "time_rationale": "Explanation of why this score was given based on available hours vs project scale.",
    "budget_score": 5,
    "budget_rationale": "Explanation based on budget vs resource/hosting/development costs.",
    "skill_score": 6,
    "skill_rationale": "Explanation based on existing skills vs skill gap required for this project.",
    "overall_score": 6,
    "overall_rationale": "Synthesized feasibility score representing overall viability."
  }},
  "risks": {{
    "technical": {{
      "description": "Primary technical risk (e.g. database scaling, complex APIs, offline sync).",
      "mitigation": "How to mitigate this technical risk (e.g. use simple Django views, SQLite, start small)."
    }},
    "resource": {{
      "description": "Resource constraint risk (e.g. running out of time, server costs, software licensing).",
      "mitigation": "How to mitigate this resource risk."
    }},
    "market": {{
      "description": "Market adoption or user interest risk.",
      "mitigation": "How to mitigate this market risk (e.g. release a landing page first, run interviews)."
    }},
    "skills": {{
      "description": "Gaps between existing skills and skills needed for the project.",
      "mitigation": "Specific mitigation for learning/outsourcing the gaps."
    }}
  }},
  "scenarios": {{
    "optimistic": {{
      "outcome": "What happens if things go exceptionally well (e.g. rapid MVP build, high early conversion).",
      "probability": 80,
      "factors": ["Dedicated time allocation", "Prompt feedback from initial users", "Stable API usage"]
    }},
    "realistic": {{
      "outcome": "Most likely progress timeline and milestones achieved.",
      "probability": 55,
      "factors": ["Typical development delays", "Balancing with other life commitments", "Small budget adjustments"]
    }},
    "pessimistic": {{
      "outcome": "What happens if roadblocks occur (e.g. API changes, severe time crunch, database corruption).",
      "probability": 25,
      "factors": ["Unexpected system outages", "Loss of motivation", "Scope creep beyond MVP"]
    }}
  }},
  "roadmap": {{
    "day_30": {{
      "milestone": "Core Milestone 1 (e.g., Working Wireframe & Core DB Schema)",
      "tasks": [
        "Task 1 for the first 30 days.",
        "Task 2 for the first 30 days.",
        "Task 3 for the first 30 days."
      ]
    }},
    "day_60": {{
      "milestone": "Core Milestone 2 (e.g., MVP Core Flow & Mock Integrations)",
      "tasks": [
        "Task 1 for the second month.",
        "Task 2 for the second month.",
        "Task 3 for the second month."
      ]
    }},
    "day_90": {{
      "milestone": "Core Milestone 3 (e.g., Deploy to Beta & Collect Feedback)",
      "tasks": [
        "Task 1 for the third month.",
        "Task 2 for the third month.",
        "Task 3 for the third month."
      ]
    }}
  }},
  "first_action": "Generate exactly ONE immediate action the user should take today. Make it highly action-oriented and concrete.",
  "confidence_level": "High"
}}

Ensure all scores are integers between 1 and 10.
Ensure risk_level is an integer between 1 and 10.
Ensure confidence_score is an integer between 0 and 100.
Ensure success probabilities are integers between 0 and 100.
Ensure confidence_level is exactly one of 'High', 'Medium', 'Low'.
Keep rationales and descriptions concise but professional and realistic. Output ONLY valid JSON.
"""

    generation_config = {
        "response_mime_type": "application/json"
    }

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        result_text = response.text.strip()
        analysis_data = json.loads(result_text)
        analysis_data["is_fallback"] = False
        return analysis_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON output: {e}. Output was: {response.text}")
        raise ValueError("The AI model returned an invalid response format. Please try again.")
    except Exception as e:
        logger.error(f"Error communicating with Gemini API: {e}. Falling back to mock generator.")
        # Check if the key is missing entirely, in which case we raise it to force configuration,
        # otherwise we fallback for quota/network errors.
        if "API Key is not configured" in str(e):
            raise ValueError(str(e))
        
        fallback_data = generate_mock_fallback_analysis(
            idea_name, description, time_available, budget, skills, goal
        )
        fallback_data["is_fallback"] = True
        return fallback_data

def generate_mock_fallback_analysis(idea_name, description, time_available, budget, skills, goal):
    """
    Generates a high-quality, customized mock analysis when the Gemini API is rate-limited or out of quota.
    """
    return {
        "problem_statement": f"Friction and inefficiencies in executing '{idea_name}' due to high entry barriers, resource limitations, and planning complexity.",
        "target_audience": f"Early adopters and consumers of '{idea_name}' who experience the core frustration of: '{description[:80]}...'",
        "value_proposition": f"A streamlined approach to '{idea_name}' leveraging your existing skills ('{skills}') to achieve the milestone of '{goal}' efficiently.",
        "key_assumptions": [
            f"Target users are actively looking for a simplified solution like '{idea_name}'.",
            f"The goal of '{goal}' can be successfully prototyped within a budget of ${budget}.",
            f"Allocating {time_available} hours per week is sufficient to construct and test the initial core flow."
        ],
        "readiness_interpretation": f"Your project shows moderate readiness. Leveraging skills like '{skills}' provides a strong head start, but the constraints of {time_available} hours/week and a budget of ${budget} will require disciplined scoping to launch in a reasonable timeframe.",
        "risk_level": 5,
        "confidence_score": 78,
        "confidence_reasoning": f"Based on the alignment of skills ('{skills}') and budget constraints (${budget}), standard parameters indicate moderate execution confidence.",
        "assumptions": [
            {
                "category": "User",
                "assumption": f"Target users will actively engage with '{idea_name}' on a weekly basis.",
                "risk": "Medium",
                "explanation": "Retention can drop off rapidly if the user onboarding is complex or lacks immediate value.",
                "validation_recommendation": f"Conduct user interviews with 5 potential adopters of '{idea_name}' to map their expectations."
            },
            {
                "category": "Market",
                "assumption": f"There is sufficient commercial demand to validate the budget of ${budget}.",
                "risk": "Medium",
                "explanation": "Competitors might satisfy the general need, making user acquisition costly.",
                "validation_recommendation": "Publish a landing page describing the product and track the email sign-up conversion rate."
            },
            {
                "category": "Technical",
                "assumption": f"Your current skills ('{skills}') are sufficient to implement the core product.",
                "risk": "Low",
                "explanation": f"The core components align with your skills ('{skills}'). Minimal third-party API dependencies keep complexity low.",
                "validation_recommendation": "Draft a system architecture map and test connections to necessary external API services."
            },
            {
                "category": "Resource",
                "assumption": f"Allocating {time_available} hours/week is sufficient to build and launch the project.",
                "risk": "High",
                "explanation": "Balancing execution with other professional or personal commitments frequently causes milestone delays.",
                "validation_recommendation": "Break the first month down into 4 weekly sub-milestones and track hours spent on each."
            }
        ],
        "feasibility": {
            "time_score": 7 if time_available >= 10 else 4,
            "time_rationale": f"An allocation of {time_available} hours per week allows steady progress for a solo builder, though scaling will require operations optimization.",
            "budget_score": 8 if budget >= 1000 else (5 if budget >= 250 else 3),
            "budget_rationale": f"A budget of ${budget} is sufficient to buy hosting, glass packaging or standard APIs, but limits outsourcing custom developer labor.",
            "skill_score": 7,
            "skill_rationale": f"Leveraging your skills ('{skills}') provides a strong setup. Online code repositories or templates will fill initial technical gaps.",
            "overall_score": 7,
            "overall_rationale": f"Viability is positive. Commencing with a manual concierge service or a mockup fits your constraints perfectly and minimizes early risks."
        },
        "risks": {
            "technical": {
                "description": f"Over-engineering the technical structure of '{idea_name}' beyond the required prototype scope.",
                "mitigation": "Launch as a single-page responsive web app first, using standard templates and manual database records."
            },
            "resource": {
                "description": f"Running out of cash within the ${budget} budget or burning out with only {time_available} hours/week.",
                "mitigation": "Define a strict list of features and focus solely on the most important core capability."
            },
            "market": {
                "description": f"Lack of demand or failure to interest the target audience in '{idea_name}'.",
                "mitigation": f"Before coding, conduct interviews with 5 potential users to validate the primary value proposition."
            },
            "skills": {
                "description": f"Gaps in technical implementation for '{description[:40]}...'",
                "mitigation": "Use no-code automation integrations (e.g., Zapier) to handle database workflows initially."
            }
        },
        "scenarios": {
            "optimistic": {
                "outcome": f"Successfully launch the prototype, securing '{goal}' within the first 6 weeks.",
                "probability": 75,
                "factors": ["High demand in local networks", "Flawless tool integrations", "Zero critical bugs"]
            },
            "realistic": {
                "outcome": f"Achieve '{goal}' in 10-12 weeks with typical learning delays and adjustments.",
                "probability": 50,
                "factors": ["Balancing commitments with secondary work", "Step-by-step user feedback integration"]
            },
            "pessimistic": {
                "outcome": f"Slow onboarding and high friction, resulting in under 10% of '{goal}' completed by day 90.",
                "probability": 25,
                "factors": ["Scope creep beyond basic prototype", "High user drop-off during onboarding"]
            }
        },
        "roadmap": {
            "day_30": {
                "milestone": "Define Core Concept & Launch Landing Page",
                "tasks": [
                    f"Create a simple landing page explaining the core benefits of '{idea_name}'.",
                    "Share the signup link with 10 potential users in your target audience.",
                    "Collect feedback and compile a prioritised list of feature requests."
                ]
            },
            "day_60": {
                "milestone": "Implement Core Functionality & Test Run",
                "tasks": [
                    f"Assemble a manual mockup of '{idea_name}' using basic Django and SQLite.",
                    "Onboard the first 5 beta users to test the delivery loop.",
                    "Manually resolve errors and adjust layout based on active usage."
                ]
            },
            "day_90": {
                "milestone": f"Scale & Achieve Primary Goal: '{goal}'",
                "tasks": [
                    "Integrate payment links or feedback forms on the active dashboard.",
                    "Run marketing campaigns in niche communities where target users hang out.",
                    "Analyze conversion metrics to determine whether to pivot or scale up."
                ]
            }
        },
        "first_action": f"Draft a simple layout document outlining target features of '{idea_name}' and share it with 3 peers today.",
        "confidence_level": "Medium"
    }
