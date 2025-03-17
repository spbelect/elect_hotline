import prometheus_client


emails_sent = prometheus_client.Counter(
    'django_emails_sent_total',
    documentation = 'Total number of emails sent',
    labelnames = ['destination']
)
