#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from apps.videos.models import Video

from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages import video_page
from apps.webdriver_testing.pages.site_pages import video_language_page
from apps.webdriver_testing.pages.site_pages import editor_page
from apps.webdriver_testing.pages.editor_pages import dialogs
from apps.webdriver_testing.pages.editor_pages import unisubs_menu
from apps.webdriver_testing.pages.editor_pages import subtitle_editor 
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import TaskFactory
from apps.webdriver_testing.data_factories import WorkflowFactory
from apps.webdriver_testing.pages.site_pages.teams.tasks_tab import TasksTab
from apps.webdriver_testing.data_factories import TeamVideoFactory
from apps.webdriver_testing.data_factories import TeamMemberFactory


class TestCaseEntryExit(WebdriverTestCase):
    """Entry and Exit points to New Editor. """
    fixtures = ['apps/webdriver_testing/fixtures/editor_auth.json', 
                'apps/webdriver_testing/fixtures/editor_videos.json',
                'apps/webdriver_testing/fixtures/editor_subtitles.json']
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseEntryExit, cls).setUpClass()
        cls.logger.info("""Default Test Data - loaded from fixtures

                        English, source primary v2 -> v6
                                 v1 -> deleted

                        Chinese v1 -> v3
                                v3 {"zh-cn": 2, "en": 6}

                        Danish v1 --> v4
                               v4 {"en": 5, "da": 3}
                               
                        Swedish v1 --> v3 FORKED
                                v3 {"sv": 2}
                                v1 --> private

                        Turkish (tr) v1 incomplete {"en": 5}
                       """)

        
        cls.create_modal = dialogs.CreateLanguageSelection(cls)
        cls.sub_editor = subtitle_editor.SubtitleEditor(cls)
        cls.unisubs_menu = unisubs_menu.UnisubsMenu(cls)
        cls.editor_pg = editor_page.EditorPage(cls)
        cls.video_pg = video_page.VideoPage(cls)
        cls.video_lang_pg = video_language_page.VideoLanguagePage(cls)
        cls.tasks_tab = TasksTab(cls)

        cls.user = UserFactory.create()
        cls.video_pg.open_page('videos/watch/')
        cls.video_pg.log_in(cls.user, 'password')

        #Create a workflow enabled team to check review/approve dialog switching.
        cls.team = TeamMemberFactory.create(team__workflow_enabled=True,
                                            team__translate_policy=20, #any team
                                            team__subtitle_policy=20, #any team
                                            team__task_assign_policy=10, #any team
                                            user = cls.user,
                                            ).team
        cls.workflow = WorkflowFactory(team = cls.team,
                                       autocreate_subtitle=True,
                                       autocreate_translate=True,
                                       approve_allowed = 10, # manager
                                       review_allowed = 10, # peer
                                       )



    def tearDown(self):
        self.browser.get_screenshot_as_file("MYTMP/%s.png" % self.id())
        self.video_pg.open_page('videos/watch/')
        self.video_pg.handle_js_alert('accept')

    def test_timed_to_new(self):
        """From timed editor to beta, reference and working langs are same.

        """
        video = Video.objects.all()[0]
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.edit_subtitles()
        self.sub_editor.open_in_beta_editor()
        self.assertEqual('English', self.editor_pg.selected_ref_language())
        self.assertEqual('English subtitles', 
                          self.editor_pg.working_language())

    def test_timed_to_new_back_to_full(self):
        """From timed editor to beta, reference and working langs are same.

        """
        video = Video.objects.all()[0]
        self.video_lang_pg.open_video_lang_page(video.video_id, 'en')
        self.video_lang_pg.edit_subtitles()
        self.sub_editor.open_in_beta_editor()
        self.assertEqual('English', self.editor_pg.selected_ref_language())
        self.editor_pg.exit_to_full_editor()
        self.assertEqual('Typing', self.sub_editor.dialog_title())

    def test_forked_to_new(self):
        """Translation editor to beta, reference lang and version is source.

        """
        video = Video.objects.all()[0]
        self.video_lang_pg.open_video_lang_page(video.video_id, 'sv')
        self.video_lang_pg.edit_subtitles()
        self.sub_editor.open_in_beta_editor()
        self.assertEqual('Swedish', self.editor_pg.selected_ref_language())
        self.assertEqual('Version 3', self.editor_pg.selected_ref_version())
        self.assertEqual('Swedish subtitles', 
                          self.editor_pg.working_language())


    def test_review_to_new(self):
        video = Video.objects.all()[0]
        #Add video to team and create a review task
        tv = TeamVideoFactory(team=self.team, added_by=self.user, video=video)
        translate_task = TaskFactory.build(type = 20, 
                           team = self.team, 
                           team_video = tv, 
                           language = 'sv', 
                           assignee = self.user)

        translate_task.new_subtitle_version = translate_task.get_subtitle_version()
        translate_task.save()
        task = translate_task.complete()
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Review Swedish Subtitles', 
                                               video.title)
        self.sub_editor.continue_to_next_step()
        self.sub_editor.open_in_beta_editor()
        self.assertEqual('Swedish', self.editor_pg.selected_ref_language())
        self.assertEqual('Version 3', self.editor_pg.selected_ref_version())
        self.assertEqual('Swedish subtitles', 
                          self.editor_pg.working_language())

    def test_review_to_new_back_to_full(self):
        """Start Review task, switch to new editor and back to Review.

        """

        video = Video.objects.all()[0]
        #Add video to team and create a review task
        tv = TeamVideoFactory(team=self.team, added_by=self.user, video=video)
        translate_task = TaskFactory.build(type = 20, 
                           team = self.team, 
                           team_video = tv, 
                           language = 'sv', 
                           assignee = self.user)
        translate_task.new_subtitle_version = translate_task.get_subtitle_version()
        translate_task.save()
        task = translate_task.complete()
        self.tasks_tab.open_tasks_tab(self.team.slug)
        self.tasks_tab.perform_and_assign_task('Review Swedish Subtitles', 
                                               video.title)
        self.sub_editor.continue_to_next_step()
        self.sub_editor.open_in_beta_editor()
        self.assertEqual('Swedish', self.editor_pg.selected_ref_language())
        self.assertEqual('Version 3', self.editor_pg.selected_ref_version())
        self.editor_pg.exit_to_full_editor()
        self.assertEqual('Review subtitles', self.sub_editor.dialog_title())




        
        

