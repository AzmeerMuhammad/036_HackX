"""
Management command to create demo data:
- 6-10 verified professionals
- 6-10 SOP documents
- Demo users
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.professionals.models import Professional, ProfessionalSOPDoc


class Command(BaseCommand):
    help = 'Create demo data: professionals, SOP docs, and demo users'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')
        
        # Create demo users
        demo_users = [
            {'username': 'demo_user', 'password': 'demo123', 'display_name': 'Demo User', 'email': 'demo@example.com'},
            {'username': 'test_user', 'password': 'test123', 'display_name': 'Test User', 'email': 'test@example.com'},
        ]
        
        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'display_name': user_data['display_name'],
                    'email': user_data['email'],
                    'is_anonymous_mode': True
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
        
        # Create verified professionals
        professionals_data = [
            {
                'username': 'dr_ahmed',
                'display_name': 'Dr. Ahmed Khan',
                'email': 'ahmed@psifi.com',
                'specialization': 'Clinical Psychology',
                'city': 'Karachi',
                'availability': 'Mon-Fri 9AM-5PM',
            },
            {
                'username': 'dr_fatima',
                'display_name': 'Dr. Fatima Ali',
                'email': 'fatima@psifi.com',
                'specialization': 'Psychiatry',
                'city': 'Lahore',
                'availability': 'Mon-Sat 10AM-6PM',
            },
            {
                'username': 'dr_hamza',
                'display_name': 'Dr. Hamza Malik',
                'email': 'hamza@psifi.com',
                'specialization': 'Counseling Psychology',
                'city': 'Islamabad',
                'availability': 'Mon-Fri 8AM-4PM',
            },
            {
                'username': 'dr_sana',
                'display_name': 'Dr. Sana Sheikh',
                'email': 'sana@psifi.com',
                'specialization': 'Child Psychology',
                'city': 'Karachi',
                'availability': 'Tue-Sat 9AM-5PM',
            },
            {
                'username': 'dr_umar',
                'display_name': 'Dr. Umar Hassan',
                'email': 'umar@psifi.com',
                'specialization': 'Trauma Therapy',
                'city': 'Lahore',
                'availability': 'Mon-Thu 11AM-7PM',
            },
            {
                'username': 'dr_zainab',
                'display_name': 'Dr. Zainab Qureshi',
                'email': 'zainab@psifi.com',
                'specialization': 'Anxiety Disorders',
                'city': 'Islamabad',
                'availability': 'Mon-Fri 9AM-5PM',
            },
            {
                'username': 'dr_ali',
                'display_name': 'Dr. Ali Raza',
                'email': 'ali@psifi.com',
                'specialization': 'Depression Treatment',
                'city': 'Karachi',
                'availability': 'Mon-Sat 10AM-6PM',
            },
            {
                'username': 'dr_ayesha',
                'display_name': 'Dr. Ayesha Malik',
                'email': 'ayesha@psifi.com',
                'specialization': 'Family Therapy',
                'city': 'Lahore',
                'availability': 'Mon-Fri 9AM-5PM',
            },
        ]
        
        for prof_data in professionals_data:
            user, created = User.objects.get_or_create(
                username=prof_data['username'],
                defaults={
                    'display_name': prof_data['display_name'],
                    'email': prof_data['email'],
                    'is_anonymous_mode': False
                }
            )
            if created:
                user.set_password('professional123')
                user.is_professional = True
                user.professional_type = 'psychiatrist'  # Default, can be customized
                user.save()
            
            professional, created = Professional.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': prof_data['specialization'],
                    'city': prof_data['city'],
                    'availability': prof_data['availability'],
                    'verified': True
                }
            )
            if not created:
                professional.verified = True
                professional.save()
            
            self.stdout.write(self.style.SUCCESS(f'Created professional: {professional.user.display_name}'))
        
        # Create SOP documents
        sop_docs = [
            {
                'title': 'Anxiety Support Guidelines',
                'category': 'anxiety',
                'content': '''
                When a user expresses anxiety:
                1. Acknowledge their feelings with empathy
                2. Ask about specific triggers or situations
                3. Inquire about physical symptoms (breathing, heart rate)
                4. Ask about duration and frequency
                5. NEVER provide medical advice or diagnosis
                6. If severe, escalate to professional
                7. Focus on gathering information and providing emotional support
                ''',
            },
            {
                'title': 'Depression Support Guidelines',
                'category': 'depression',
                'content': '''
                When a user expresses depression:
                1. Listen empathetically without judgment
                2. Ask about sleep patterns and appetite
                3. Inquire about daily activities and motivation
                4. Ask about support systems (family, friends)
                5. NEVER suggest specific treatments or medications
                6. If severe or persistent, escalate to professional
                7. Provide emotional support and validation
                ''',
            },
            {
                'title': 'Self-Harm Risk Assessment',
                'category': 'self-harm-risk',
                'content': '''
                When self-harm risk is detected:
                1. Express immediate concern for their safety
                2. Ask if they have a plan or means
                3. Inquire about previous attempts or thoughts
                4. Ask about support systems available
                5. NEVER minimize or dismiss their feelings
                6. IMMEDIATELY escalate to professional
                7. Provide crisis resources if available
                8. Emphasize that help is available
                ''',
            },
            {
                'title': 'Panic Attack Support',
                'category': 'panic',
                'content': '''
                When panic is expressed:
                1. Acknowledge the overwhelming nature of panic
                2. Ask about physical symptoms (breathing, chest tightness)
                3. Inquire about triggers or situations
                4. Ask about frequency and duration
                5. NEVER provide medical diagnosis
                6. If severe or frequent, escalate to professional
                7. Provide calming reassurance
                ''',
            },
            {
                'title': 'Stress Management Support',
                'category': 'stress',
                'content': '''
                When stress is expressed:
                1. Validate their feelings
                2. Ask about sources of stress (work, relationships, etc.)
                3. Inquire about coping mechanisms currently used
                4. Ask about impact on daily life
                5. NEVER prescribe specific solutions
                6. If overwhelming, escalate to professional
                7. Provide empathetic listening
                ''',
            },
            {
                'title': 'Relationship Issues Support',
                'category': 'relationships',
                'content': '''
                When relationship issues are expressed:
                1. Listen without taking sides
                2. Ask about specific concerns or conflicts
                3. Inquire about communication patterns
                4. Ask about impact on mental health
                5. NEVER provide relationship advice
                6. If causing significant distress, escalate to professional
                7. Provide emotional support
                ''',
            },
            {
                'title': 'Sleep Issues Support',
                'category': 'sleep',
                'content': '''
                When sleep issues are expressed:
                1. Acknowledge the impact of poor sleep
                2. Ask about sleep patterns (duration, quality)
                3. Inquire about factors affecting sleep
                4. Ask about impact on daily functioning
                5. NEVER prescribe sleep medications
                6. If severe or chronic, escalate to professional
                7. Provide empathetic support
                ''',
            },
            {
                'title': 'General Emotional Support',
                'category': 'general',
                'content': '''
                General support guidelines:
                1. Always be empathetic and non-judgmental
                2. Ask open-ended questions to understand the situation
                3. Validate their feelings and experiences
                4. Gather relevant information about their state
                5. NEVER provide medical advice, diagnosis, or treatment
                6. Escalate if risk is detected or if professional help is needed
                7. Focus on listening, understanding, and connecting to appropriate resources
                ''',
            },
        ]
        
        # Get first professional to assign SOPs
        first_professional = Professional.objects.filter(verified=True).first()
        
        for sop_data in sop_docs:
            sop, created = ProfessionalSOPDoc.objects.get_or_create(
                title=sop_data['title'],
                defaults={
                    'category': sop_data['category'],
                    'content': sop_data['content'],
                    'created_by_professional': first_professional,
                    'active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created SOP: {sop.title}'))
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write('\nDemo User Credentials:')
        self.stdout.write('  Username: demo_user, Password: demo123')
        self.stdout.write('  Username: test_user, Password: test123')
        self.stdout.write('\nProfessional Credentials:')
        self.stdout.write('  Username: dr_ahmed, Password: professional123')
        self.stdout.write('  (All professionals use password: professional123)')

