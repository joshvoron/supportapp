import uuid
import random
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.groups.models import GroupModel, BotModel, RequestModel, MessageModel
from apps.agents.models import AgentModel
from apps.users.models import UserModel
from apps.clients.models import ClientModel

fake = Faker()


class Command(BaseCommand):
    help = 'Fill database with fake test data'

    def handle(self, *args, **kwargs):
        try:
            if AgentModel.objects.all().exists():
                return
            self.create_agents()
            self.create_clients()
            self.create_bots()
            self.create_groups()
            self.create_requests()
            self.create_messages()
            self.create_superuser()
            self.stdout.write(self.style.SUCCESS("✅✅✅ BD Data was created!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR('❌ Something went wrong! '
                                               f'Error: {e}'))

    def create_agents(self, n=10):
        for _ in range(n):
            AgentModel.objects.create(
                username=fake.user_name(),
                email=fake.email(),
                name=fake.first_name(),
                surname=fake.last_name(),
            )
        self.stdout.write(self.style.SUCCESS("✅ Agents were created"))

    def create_clients(self, n=5):
        for _ in range(n):
            ClientModel.objects.create(
                name=fake.user_name(),
                telegram_id=random.randrange(1000000, 10000000)
            )
        self.stdout.write(self.style.SUCCESS("✅ Clients were created"))

    def create_bots(self, n=1):
        for _ in range(n):
            BotModel.objects.create(
                name=fake.sentence(nb_words=2),
                secret_key=uuid.UUID("e387d905-7ea4-4d37-8ee9-eff4a083e6b9")
            )
        self.stdout.write(self.style.SUCCESS("✅ Bots were created"))

    def create_groups(self, n=1):
        agents = list(AgentModel.objects.all())
        bots = list(BotModel.objects.all())
        for _ in range(n):
            group = GroupModel.objects.create(
                owner=random.choice(agents),
                name=fake.sentence(nb_words=2),
            )
            group.agents.set(random.sample(agents, k=5))
            group.bots.set(random.sample(bots, k=1))
            group.save()
        self.stdout.write(self.style.SUCCESS("✅ Groups were created"))

    def create_requests(self, n=7):
        clients = list(ClientModel.objects.all())
        agents = list(AgentModel.objects.all())
        bots = list(BotModel.objects.all())

        now = timezone.now()

        for _ in range(n):
            random_offset = timedelta(
                days=random.randint(0, 30))
            random_time = now - random_offset
            is_solved = random.choice([True, False])
            solved_by = random.choice(agents) if is_solved else None
            RequestModel.objects.create(
                client=random.choice(clients),
                is_solved=is_solved,
                solved_by=solved_by,
                theme=fake.sentence(nb_words=2),
                bot=random.choice(bots),
                created=random_time,
                rate=random.choice([1, 2, 3, 4, 5, None])
            )
        self.stdout.write(self.style.SUCCESS("✅ Requests were created"))

    def create_superuser(self):
        # Superuser creation
        if AgentModel.objects.filter(username="admin").exists():
            return
        superuser = AgentModel.objects.create(
            username="admin",
            email="superuser@mail.com",
            name="Admin",
            surname="Super",
            is_superuser=True,
            is_staff=True,
        )
        superuser.set_password("superuser")
        superuser.save()

        # Adds superuser to groups
        groups = GroupModel.objects.all()
        for group in groups:
            group.agents.add(superuser)

        self.stdout.write(self.style.SUCCESS("✅ Superuser was created"))

    def create_messages(self, n=200):
        users = list(UserModel.objects.all())
        requests = list(RequestModel.objects.all())

        now = timezone.now()

        for _ in range(n):
            random_offset = timedelta(
                seconds=random.randint(0, 3600))  # 1 hour
            random_time = now - random_offset
            MessageModel.objects.create(
                text=fake.sentence(nb_words=6),
                user=random.choice(users),
                request=random.choice(requests),
                sended=random_time
            )
        self.stdout.write(self.style.SUCCESS("✅ Messages were created"))
