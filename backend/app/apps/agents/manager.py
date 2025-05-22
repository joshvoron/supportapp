from django.contrib.auth.base_user import BaseUserManager


class AgentManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, email, name,
                     **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, name=name,
                          **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password, email, name, **extra_fields):
        return self._create_user(username, password, email, name,
                                 **extra_fields)
