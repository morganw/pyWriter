from django import forms
from tinymce.widgets import TinyMCE
from .models import Artifact, Chapter, Character, Location, Scene, Story
from .widgets import AgkaniCoverWidget


class SceneForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop(
            'user', None)  # get user for the scene form to limit the content
        super(SceneForm, self).__init__(*args, **kwargs)  # populates the post

        self.fields[
            'perspective'].queryset = Character.objects.filter(user=self.user)
        self.fields['chapter'].queryset = Chapter.objects.filter(
            user=self.user)
        self.fields[
            'characters'].queryset = Character.objects.filter(user=self.user)
        self.fields['location'].queryset = Location.objects.filter(
            user=self.user)
        self.fields[
            'artifacts'].queryset = Artifact.objects.filter(user=self.user)

    description = forms.CharField(widget=TinyMCE(), help_text="Enter a simple description of the scene")
    content = forms.CharField(widget=TinyMCE(
        attrs={'cols': 100, 'rows': 30},
        mce_attrs={
            'theme': 'advanced',
            'theme_advanced_buttons1' : "bold,italic,underline,separator,strikethrough,justifyleft,justifycenter,justifyright, justifyfull,bullist,numlist,undo,redo,indent,outdent,sup,sub,charmap",
            'theme_advanced_buttons2' : "",
            'theme_advanced_buttons3' : "",

            'theme_advanced_toolbar_align' : "left",  
            'theme_advanced_toolbar_location': 'top',
            'theme_advanced_statusbar_location': 'bottom',
            'plugins': 'wordcount,fullscreen',
            'theme_advanced_buttons1_add' : "fullscreen",}
        ))
    scene_start_time = forms.DateTimeField(required=False, widget=forms.DateInput(attrs={'class':'timepicker'}))
    scene_end_time = forms.DateTimeField(required=False, widget=forms.DateInput(attrs={'class':'timepicker'}))
    
    class Meta:
        model = Scene
        fields = ('name', 'word_target', 'status', 'importance', 'perspective', 'chapter', 'description', 'characters', 'location', 'artifacts', 'content', 'scene_start_time', 'scene_end_time')


class CharacterForm(forms.ModelForm):
    
    class Meta:
        model = Character
        fields = (
            'firstname', 'middlename', 'lastname', 'nicknames',
            'role', 'major_character', 'description', 'image',
            'bio', 'date_of_birth', 'date_of_death'
            )


class LocationForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ('name', 'description', 'image', 'date_of_construction', 'date_of_destruction')


class ArtifactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop(
            'user', None)  # get user for the scene form to limit the content
        super(
            ArtifactForm, self).__init__(*args, **kwargs)  # populates the post

        self.fields['owner'].queryset = Character.objects.filter(
            user=self.user)
        self.fields['location'].queryset = Location.objects.filter(
            user=self.user)

    class Meta:
        model = Artifact
        fields = ('name', 'description', 'image', 'owner', 'location', 'date_of_construction', 'date_of_destruction')


class StoryForm(forms.ModelForm):

    class Meta:
        model = Story
        fields = ('title', 'author', 'synopsis', 'genre', 'fiction', 'cover', 'registered_access', 'public_access')
        widgets = {'cover' : AgkaniCoverWidget}


class ChapterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop(
            'user', None)  # get user for the scene form to limit the content
        super(
            ChapterForm, self).__init__(*args, **kwargs)  # populates the post

        self.fields['story'].queryset = Story.objects.filter(user=self.user)

    class Meta:
        model = Chapter
        fields = ('story', 'title', 'weight')
