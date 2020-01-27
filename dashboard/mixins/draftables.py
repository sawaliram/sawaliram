from django.db import models

# Generic draftable mixin
# "Draftables" are things that go through the three stages of
# draft -> submitted -> published

class PublishedDraftableManager(models.Manager):
    def get_queryset(self):
        return (super()
            .get_queryset()
            .filter(status=self.model.STATUS_PUBLISHED))

class DraftDraftableManager(models.Manager):
    def get_queryset(self):
        return (super()
            .get_queryset()
            .filter(status=self.model.STATUS_DRAFT))

class SubmittedDraftableManager(models.Manager):
    def get_queryset(self):
        return (super()
            .get_queryset()
            .filter(status=self.model.STATUS_SUBMITTED))

class DraftableModel(models.Model):
    '''
    Generic mixin for all "draftable" items - that is, items which go
    through the three states of "draft", "submitted" and "published".
    '''

    class Meta:
        abstract = True

    # Statuses

    STATUS_DRAFT = -1
    STATUS_SUBMITTED = 0
    STATUS_PUBLISHED = 1

    # Fields

    status = models.IntegerField(default=-1) # draft

    # Managers

    objects = models.Manager()
    get_published = PublishedDraftableManager()
    get_drafts = DraftDraftableManager()
    get_submitted = SubmittedDraftableManager()

    @property
    def is_draft(self):
        return self.status == self.STATUS_DRAFT

    @property
    def is_submitted(self):
        return self.status == self.STATUS_SUBMITTED

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    @classmethod
    def get_draft_model(cls):
        class DraftMixin:

            def __init__(self, *args, **kwargs):
                self._meta.get_field('status').default = self.STATUS_DRAFT
                super().__init__(*args, **kwargs)

            def submit_draft(self):
                '''
                Submit the draft. That is, change the status of the
                current object to STATUS_SUBMITTED and return it.
                '''

                try:
                    self.status = self.STATUS_SUBMITTED
                    self.save()
                except Exception as e:
                    error = 'Error submitting: {}'.format(e)
                    print(error)
                    raise e

                return cls.objects.get(id=self.id)

        # Return the mixin
        return DraftMixin

    @classmethod
    def get_submitted_model(cls):
        class SubmittedMixin:

            def __init__(self, *args, **kwargs):
                self._meta.get_field('status').default = self.STATUS_SUBMITTED
                super().__init__(*args, **kwargs)

            def publish(self, approved_by):
                '''
                Publish the submission. That is, change the status
                of the current object to STATUS_PUBLISHED and set
                the approved_by attribute
                '''

                try:
                    self.approved_by = approved_by
                    self.status = self.STATUS_SUBMITTED
                    self.save()
                except Exception as e:
                    error = 'Error publishing: {}'.format(e)
                    print(error)
                    raise e

                return cls(self.id)

        # Return the mixin
        return SubmittedMixin

    @classmethod
    def get_published_model(cls):
        class PublishedMixin:

            def __init__(self, *args, **kwargs):
                self._meta.get_field('status').default = self.STATUS_PUBLISHED
                super().__init__(*args, **kwargs)

        # Return the mixin
        return PublishedMixin
