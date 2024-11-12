# Generated by Django 3.0.5 on 2020-05-12 17:15

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import ufo.models.websiteuser
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('country', models.CharField(choices=[('ru', 'Россия'), ('ua', 'Украина'), ('bg', 'Беларусь'), ('kz', 'Казахстан')], default='ru', max_length=2)),
                ('utc_offset', models.SmallIntegerField(default=3)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', ufo.models.websiteuser.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=40, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('timestamp', models.DateTimeField(verbose_name='Когда пользователь ввел ответ')),
                ('revoked', models.BooleanField(default=False, verbose_name='отозвано')),
                ('is_incident', models.BooleanField()),
                ('role', models.CharField(max_length=15)),
                ('uik', models.SmallIntegerField()),
                ('uik_complaint_status', models.SmallIntegerField(choices=[(223, 'не подавалась'), (30513, 'отказ принять жалобу'), (10047, 'отказ рассмотрения жалобы'), (13478, 'отказ выдать копию решения'), (14958, 'ожидание решения комиссии'), (24833, 'получено неудовлетворительное решение'), (32722, 'получено удовлетворительное решение')], default=223)),
                ('tik_complaint_status', models.SmallIntegerField(choices=[(223, 'не подавалась'), (19091, 'ожидает модератора'), (16978, 'отклонено'), (1546, 'email отправлен')], default=223)),
                ('tik_complaint_text', models.TextField(blank=True, null=True)),
                ('time_tik_email_request_created', models.DateTimeField(blank=True, null=True)),
                ('value_bool', models.BooleanField(blank=True, null=True)),
                ('value_int', models.IntegerField(blank=True, null=True)),
                ('banned', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
            ],
            options={
                'ordering': ('election__date',),
            },
        ),
        migrations.CreateModel(
            name='ClientError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='Когда произошло')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Полученный JSON')),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('uiks', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), blank=True, null=True, size=None)),
                ('name', models.TextField()),
                ('telegram_channel', models.TextField()),
            ],
            options={
                'verbose_name': 'Район',
            },
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('date', models.DateField(verbose_name='Дата проведения')),
                ('country', models.CharField(choices=[('ru', 'Россия'), ('ua', 'Украина'), ('bg', 'Беларусь'), ('kz', 'Казахстан')], default='ru', max_length=2)),
                ('name', models.TextField()),
                ('flags', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MobileUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.CharField(max_length=20, unique=True)),
                ('first_name', models.TextField(blank=True, null=True)),
                ('last_name', models.TextField(blank=True, null=True)),
                ('middle_name', models.TextField(blank=True, null=True)),
                ('phone', models.TextField(blank=True, null=True)),
                ('telegram', models.TextField(blank=True, null=True)),
                ('email', models.TextField(blank=True, null=True)),
                ('role', models.CharField(blank=True, max_length=30, null=True)),
                ('uik', models.IntegerField(blank=True, null=True)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('time_last_answer', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания в БД')),
                ('name', models.CharField(max_length=1000)),
                ('shortname', models.CharField(blank=True, max_length=50, null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownerd_orgs', to=settings.AUTH_USER_MODEL)),
                ('event_streamers', models.ManyToManyField(blank=True, to='ufo.MobileUser')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('type', models.CharField(choices=[('YESNO', 'Да-Нет'), ('NUMBER', 'Число'), ('TEXT', 'Текст')], default='YESNO', max_length=20)),
                ('label', models.TextField()),
                ('fz67_text', models.TextField(blank=True, null=True)),
                ('advice_text', models.TextField(blank=True, null=True)),
                ('example_uik_complaint', models.TextField(blank=True, null=True)),
                ('elect_flags', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('limiting_questions', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('incident_conditions', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizTopic',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания')),
                ('name', models.TextField()),
                ('sortorder', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ('sortorder',),
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('name', models.TextField()),
                ('external_id', models.IntegerField(blank=True, null=True)),
                ('utc_offset', models.SmallIntegerField()),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Tik',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=40, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('name', models.TextField()),
                ('email', models.TextField(blank=True, null=True)),
                ('phone', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('uik_ranges', models.TextField()),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tiks', to='ufo.District')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tiks', to='ufo.Region')),
            ],
        ),
        migrations.CreateModel(
            name='TopicQuestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sortorder', models.PositiveSmallIntegerField(default=0)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время добавления в этот раздел')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ufo.Question')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ufo.QuizTopic')),
            ],
            options={
                'ordering': ('sortorder',),
                'unique_together': {('topic', 'question')},
            },
        ),
        migrations.CreateModel(
            name='TikSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('unsubscribed', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tik_subscriptions', to='ufo.Organization')),
                ('tik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='ufo.Tik')),
            ],
            options={
                'ordering': ['organization', 'tik__name'],
            },
        ),
        migrations.AddField(
            model_name='quiztopic',
            name='questions',
            field=models.ManyToManyField(blank=True, related_name='topics', through='ufo.TopicQuestions', to='ufo.Question'),
        ),
        migrations.CreateModel(
            name='OrgMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('operator', 'Оператор'), ('moderator', 'Модератор'), ('admin', 'Админ')], default='operator', max_length=10)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время назначения')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ufo.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrgJoinApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания заявки')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ufo.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrgBranch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uik_ranges', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='ufo.Organization')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='org_branches', to='ufo.Region')),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='join_requests',
            field=models.ManyToManyField(blank=True, related_name='org_join_requests', through='ufo.OrgJoinApplication', to=settings.AUTH_USER_MODEL, verbose_name='Заявки на вступление'),
        ),
        migrations.AddField(
            model_name='organization',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='organizations', through='ufo.OrgMembership', to=settings.AUTH_USER_MODEL, verbose_name='Члены'),
        ),
        migrations.AddField(
            model_name='organization',
            name='regions',
            field=models.ManyToManyField(blank=True, related_name='organizations', through='ufo.OrgBranch', to='ufo.Region'),
        ),
        migrations.CreateModel(
            name='Munokrug',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания записи в БД на сервере')),
                ('name', models.TextField()),
                ('uik_ranges', models.TextField(default='[]')),
                ('ikmo_email', models.TextField(blank=True, null=True)),
                ('ikmo_phone', models.TextField(blank=True, null=True)),
                ('ikmo_address', models.TextField(blank=True, null=True)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ufo.District')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='munokruga', to='ufo.Region')),
            ],
            options={
                'verbose_name': 'Мун.округ',
            },
        ),
        migrations.AddField(
            model_name='mobileuser',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ufo.Region'),
        ),
        migrations.CreateModel(
            name='ElectionMobileUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ufo.Election')),
                ('mobileuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ufo.MobileUser')),
            ],
            options={
                'unique_together': {('election', 'mobileuser')},
            },
        ),
        migrations.AddField(
            model_name='election',
            name='event_streamers',
            field=models.ManyToManyField(blank=True, related_name='elections', through='ufo.ElectionMobileUsers', to='ufo.MobileUser'),
        ),
        migrations.AddField(
            model_name='election',
            name='munokrug',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ufo.Munokrug'),
        ),
        migrations.AddField(
            model_name='election',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='elections', to='ufo.Region'),
        ),
        migrations.AddField(
            model_name='district',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ufo.Region'),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('value', models.CharField(max_length=1000)),
                ('type', models.CharField(choices=[('ph', 'Phone'), ('tg', 'Telegram'), ('wa', 'WhatsApp'), ('vk', 'VK'), ('fb', 'Facebook'), ('uk', 'Unknown')], max_length=3)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='ufo.Campaign')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='ufo.Organization')),
            ],
            options={
                'ordering': ('value',),
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='election',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns', to='ufo.Election'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to='ufo.Organization', verbose_name='Координирующая организация'),
        ),
        migrations.CreateModel(
            name='AnswerImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(choices=[('uik_complaint', 'Подаваемые в УИК жалобы'), ('uik_reply', 'Ответы, решения от УИК'), ('tik_complaint', 'Подаваемые в ТИК жалобы'), ('tik_reply', 'Ответы, решения от ТИК')], max_length=20)),
                ('filename', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('deleted_by_user', models.BooleanField(default=False)),
                ('answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='ufo.Answer')),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.AddField(
            model_name='answer',
            name='appuser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='answers', to='ufo.MobileUser'),
        ),
        migrations.AddField(
            model_name='answer',
            name='operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ufo.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ufo.Region'),
        ),
        migrations.AlterUniqueTogether(
            name='campaign',
            unique_together={('election', 'organization')},
        ),
    ]
