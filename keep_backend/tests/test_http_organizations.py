'''
    Makes HTTP requests to each of our pages to ensure there are no
    templating/etc errors on the pages.
'''
import googauth
import os

from base64 import b32encode

from django.contrib.auth.models import User
from django.core import mail

from twofactor.util import decrypt_value
from twofactor.models import UserAuthToken

from tests import HttpTestCase


class OrganizationHttpTests( HttpTestCase ):

    def test_login( self ):
        self.open( '/accounts/login' )
        assert 'Keep' in self.selenium.title

        # Generate secret token
        user = User.objects.get(username='admin')
        user_token = UserAuthToken.objects.get(user=user)
        secret_key = b32encode( decrypt_value( user_token.encrypted_seed ) )
        token = googauth.generate_code( secret_key )

        self.selenium.find_element_by_id( 'id_username' ).send_keys( 'admin' )
        self.selenium.find_element_by_id( 'id_password' ).send_keys( 'test' )
        self.selenium.find_element_by_id( 'id_token' ).send_keys( token )
        self.selenium.find_element_by_id( 'login_btn' ).click()

        assert 'admin' in self.selenium.title

    def test_create_organization( self ):
        self.test_login()

        org_name = 'test_org'

        self.selenium.find_element_by_id( 'create_org_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )

        self.selenium.find_element_by_id( 'submit-btn' ).click()

        # Check that the new org was created
        org_list = '//*[@id="org-list"]/li/a'
        orgs = self.selenium.find_elements_by_xpath( org_list )
        assert any( [ org_name in x.text for x in orgs ] )

    def test_create_organization_with_gravatar( self ):
        self.test_login()

        org_name = 'test_org_2'

        self.selenium.find_element_by_id( 'create_org_btn' ).click()
        self.selenium.find_element_by_id( 'id_gravatar' )\
                     .send_keys( 'webmaster@distributedhealth.org' )

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )
        self.selenium.find_element_by_id( 'submit-btn' ).click()

        # Check that the new repo was created
        org_list = '//*[@id="org-list"]/li/a'
        orgs = self.selenium.find_elements_by_xpath( org_list )
        assert any( [ org_name in x.text for x in orgs ] )

    def test_create_organization_fail_invalid_name( self ):

        error_msg   = 'Organization name cannot have spaces or special characters'
        org_name    = '1Q##$U ala2'

        self.test_login()
        self.selenium.find_element_by_id( 'create_org_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )
        self.selenium.find_element_by_id( 'submit-btn' ).click()

        # Check that we correctly report an error
        elem = self.selenium.find_elements_by_xpath( '//*[@class="errorlist"]/li' )
        assert any( [ x.text == error_msg for x in elem ] )

    def test_create_organization_fail_reserved_name( self ):

        error_msg   = 'Organization already exists with this name!'
        org_name    = 'new'

        self.test_login()
        self.selenium.find_element_by_id( 'create_org_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )
        self.selenium.find_element_by_id( 'submit-btn' ).click()

        # Check that we correctly report an error
        elem = self.selenium.find_elements_by_xpath( '//*[@class="errorlist"]/li' )
        assert any( [ x.text == error_msg for x in elem ] )

    def test_create_organization_fail_existing( self ):

        error_msg   = 'Organization already exists with this name!'
        org_name    = 'test_user'

        self.test_login()
        self.selenium.find_element_by_id( 'create_org_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )
        self.selenium.find_element_by_id( 'submit-btn' ).click()

        # Check that we correctly report an error
        elem = self.selenium.find_elements_by_xpath( '//*[@class="errorlist"]/li' )
        assert any( [ x.text == error_msg for x in elem ] )

    def test_organization_dashboard( self ):
        self.test_login()

        # Find the list of orgs on the page
        org_list = '//*[@id="org-list"]/li/a'
        org_list = self.selenium.find_elements_by_xpath( org_list )

        assert len( org_list ) > 0

        # Click on the first one
        first_org = org_list[0]
        first_org_name = first_org.text.strip()
        first_org.click()

        assert first_org_name in self.selenium.title

    def test_org_repo_new( self ):
        self.test_organization_dashboard()
        self.selenium.find_element_by_id( 'new_repo_btn' ).click()

        repo_name = 'xls_repo'

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( repo_name )

        xform = os.path.abspath( '_data/test_docs/tutorial.xls' )
        self.selenium.find_element_by_id( 'id_xform_file' ).send_keys( xform )

        self.selenium.find_element_by_id( 'submit_btn' ).click()

        # Check that the new repo was created
        repo_table = '/html/body/div[2]/div/div[2]/table/tbody/tr/td[2]/a'
        repos = self.selenium.find_elements_by_xpath( repo_table )
        assert any( [ x.text == repo_name for x in repos ] )
