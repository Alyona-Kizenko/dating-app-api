from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
import random
from users.models import User, UserPhoto, UserProfile
from interactions.models import Interaction, ViewHistory, Match

class Command(BaseCommand):
    help = 'Generate mock data for the dating app'
    
    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=1000, help='Number of users to create')
        parser.add_argument('--interactions', type=int, default=5000, help='Number of interactions to create')
    
    def handle(self, *args, **options):
        fake = Faker('ru_RU')
        user_count = options['users']
        interaction_count = options['interactions']
        
        self.stdout.write(f'Creating {user_count} users...')
        
        # Создаем пользователей
        users = []
        for i in range(user_count):
            gender = random.choice(['M', 'F'])
            first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
            last_name = fake.last_name_male() if gender == 'M' else fake.last_name_female()
            
            user = User(
                email=fake.unique.email(),
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                age=random.randint(18, 65),
                city=fake.city(),
                hobbies=', '.join(fake.words(nb=random.randint(3, 8))),
                status=random.choice(['looking', 'relationship', 'married', 'complicated']),
                privacy_settings=random.choice(['public', 'private', 'friends_only']),
                password=make_password('password123'),
            )
            users.append(user)
        
        User.objects.bulk_create(users, batch_size=100)
        self.stdout.write(f'Created {user_count} users')
        
        # Создаем профили для пользователей
        profiles = []
        for user in User.objects.all():
            profile = UserProfile(
                user=user,
                bio=fake.text(max_nb_chars=200),
                height=random.randint(150, 200) if random.random() > 0.3 else None,
                education=fake.word() if random.random() > 0.5 else '',
                profession=fake.job() if random.random() > 0.5 else '',
                smoking=random.random() > 0.7,
                drinking=random.random() > 0.5,
                relationship_goals=fake.text(max_nb_chars=100) if random.random() > 0.3 else '',
            )
            profiles.append(profile)
        
        UserProfile.objects.bulk_create(profiles, batch_size=100)
        self.stdout.write('Created user profiles')
        
        # Создаем взаимодействия
        self.stdout.write(f'Creating {interaction_count} interactions...')
        interactions = []
        all_users = list(User.objects.all())
        
        for _ in range(interaction_count):
            from_user = random.choice(all_users)
            to_user = random.choice([u for u in all_users if u != from_user])
            action = random.choice(['like', 'dislike', 'super_like'])
            
            interaction = Interaction(
                from_user=from_user,
                to_user=to_user,
                action=action,
            )
            interactions.append(interaction)
        
        Interaction.objects.bulk_create(interactions, batch_size=100)
        self.stdout.write(f'Created {interaction_count} interactions')
        
        # Создаем мэтчи на основе взаимных лайков
        self.stdout.write('Creating matches...')
        likes = Interaction.objects.filter(action='like')
        matches_created = 0
        
        for like in likes:
            mutual_like = Interaction.objects.filter(
                from_user=like.to_user,
                to_user=like.from_user,
                action='like'
            ).exists()
            
            if mutual_like:
                user1 = min(like.from_user, like.to_user, key=lambda u: u.id)
                user2 = max(like.from_user, like.to_user, key=lambda u: u.id)
                
                match, created = Match.objects.get_or_create(
                    user1=user1,
                    user2=user2
                )
                if created:
                    matches_created += 1
        
        self.stdout.write(f'Created {matches_created} matches')
        self.stdout.write(self.style.SUCCESS('Successfully generated mock data'))