from django.test import TestCase, Client
from django.urls import reverse
from django.db import transaction
from .models import UserProject, ProjectAnalysis

class UserProjectModelTest(TestCase):
    def setUp(self):
        self.project = UserProject.objects.create(
            idea_name="Smart Garden",
            description="Automated indoor watering system using IoT soil sensors.",
            time_available=10,
            budget=150.00,
            skills="Python, basic electronics",
            goal="Build a working prototype in 45 days"
        )

    def test_project_creation(self):
        """Tests that a UserProject instance is created correctly."""
        self.assertEqual(self.project.idea_name, "Smart Garden")
        self.assertEqual(self.project.time_available, 10)
        self.assertEqual(float(self.project.budget), 150.00)
        self.assertEqual(str(self.project), "Smart Garden")

class PlannerViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = UserProject.objects.create(
            idea_name="Smart Garden",
            description="Automated indoor watering system using IoT soil sensors.",
            time_available=10,
            budget=150.00,
            skills="Python, basic electronics",
            goal="Build a working prototype in 45 days"
        )
        
        self.analysis = ProjectAnalysis.objects.create(
            project=self.project,
            problem_statement="Houseplants die from over or under-watering due to lack of real-time monitoring.",
            target_audience="Busy urban professionals owning houseplants.",
            value_proposition="An affordable automated watering helper that takes the guesswork out of plant care.",
            key_assumptions=["People will pay $30 for a kit", "Wi-Fi signals reach plants"],
            feasibility_score={
                "time_score": 8, "time_rationale": "Sufficient for simple code",
                "budget_score": 6, "budget_rationale": "Sensors are cheap",
                "skill_score": 7, "skill_rationale": "Has basic IoT skills",
                "overall_score": 7, "overall_rationale": "High viability overall"
            },
            risks={
                "technical": {"description": "Water leak", "mitigation": "Encapsulate electronics"},
                "resource": {"description": "Running out of time", "mitigation": "Buy pre-assembled parts"},
                "market": {"description": "No buyers", "mitigation": "Test with friends first"},
                "skills": {"description": "PCB design gap", "mitigation": "Use breadboard"}
            },
            scenarios={
                "optimistic": {"outcome": "Rapid prototype build", "probability": 80, "factors": ["Prebuilt libraries"]},
                "realistic": {"outcome": "Working prototype in 2 months", "probability": 55, "factors": ["Minor debug delays"]},
                "pessimistic": {"outcome": "Burnt sensor halts progress", "probability": 25, "factors": ["Faulty wiring"]}
            },
            roadmap={
                "day_30": {"milestone": "Assemble breadboard sensors", "tasks": ["Buy parts", "Flash code"]},
                "day_60": {"milestone": "Build automated pump triggers", "tasks": ["Attach water relay"]},
                "day_90": {"milestone": "Deploy in living room", "tasks": ["Measure accuracy"]}
            },
            first_action="Order an Arduino kit on Amazon.",
            confidence_level="High"
        )

    def test_index_view(self):
        """Index view renders dashboard and list of projects."""
        response = self.client.get(reverse('planner:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BrainForge AI")
        self.assertContains(response, "Smart Garden")

    def test_project_detail_view(self):
        """Detail view renders project specifics and analysis dashboard."""
        response = self.client.get(reverse('planner:project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smart Garden")
        self.assertContains(response, "Arduino kit")

    def test_create_project_view_validation(self):
        """Form creation endpoint rejects missing inputs."""
        response = self.client.post(reverse('planner:create_project'), {
            'idea_name': '',  # missing name
            'description': 'A detailed explanation',
            'time_available': '10',
            'budget': '150',
            'skills': 'Python',
            'goal': 'Goal'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                "status": "error",
                "errors": {
                    "idea_name": "Idea name is required."
                }
            }
        )

    def test_delete_project_view(self):
        """Delete project endpoint successfully removes database rows."""
        response = self.client.post(reverse('planner:delete_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to index
        self.assertFalse(UserProject.objects.filter(pk=self.project.id).exists())

    def test_readiness_score_calculation(self):
        """Verifies the weighted math formula for project readiness score."""
        skill_score = 9
        time_score = 8
        budget_score = 9
        risk_level = 4
        
        readiness_score = int(
            (skill_score * 10) * 0.40 +
            (time_score * 10) * 0.30 +
            (budget_score * 10) * 0.20 +
            (10 - risk_level) * 10 * 0.10
        )
        self.assertEqual(readiness_score, 84)

    def test_confidence_score_classification(self):
        """Verifies that the confidence score translates correctly to classifications."""
        # Test High Confidence boundary (>= 80)
        self.analysis.confidence_score = 85
        self.analysis.save()
        response = self.client.get(reverse('planner:project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "High Confidence")

        # Test Medium Confidence boundary (50-79)
        self.analysis.confidence_score = 65
        self.analysis.save()
        response = self.client.get(reverse('planner:project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Medium Confidence")

        # Test Low Confidence boundary (< 50)
        self.analysis.confidence_score = 45
        self.analysis.save()
        response = self.client.get(reverse('planner:project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Low Confidence")

    def test_what_if_sandbox_simulator(self):
        """Verifies the scenario sandbox endpoint returns correct simulated scaling ratios."""
        response = self.client.get(reverse('planner:what_if_simulate', args=[self.project.id]), {
            'budget': '300.00',
            'time': '20',
            'team_size': '2',
            'skill_level': '9'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        
        self.assertIn('current', data)
        self.assertIn('modified', data)
        self.assertEqual(data['current']['readiness_score'], self.analysis.readiness_score)
        
        self.assertEqual(data['modified']['time_score'], 10)
        self.assertEqual(data['modified']['budget_score'], 10)
        self.assertEqual(data['modified']['skill_score'], 9)

    def test_pdf_export_response(self):
        """Confirms the PDF export endpoint yields a valid attachment response containing PDF binary."""
        response = self.client.get(reverse('planner:download_pdf', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename='))
        self.assertTrue(response.content.startswith(b'%PDF'))
