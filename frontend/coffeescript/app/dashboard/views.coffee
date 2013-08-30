define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette'

          # Model stuff
          'app/collections/views/repo'
          'app/collections/views/study'
          'app/models/study'

          # Plugins, etc.
          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette, RepoCollectionView, StudyCollectionView, StudyModel ) ->

    class StudySettingsModal extends Backbone.Modal
        template: _.template( $( '#study-settings-template' ).html() )
        cancelEl: '.btn-primary'

        initialize: ( options ) ->
            @collection = options.collection
            @study = options.study

        delete_event: ( event ) =>
            @collection.remove( @study )
            @study.destroy()
            @close()

        onRender: () =>
            $( '.study-name', @el ).html( @study.get( 'name' ) )
            $( '.study-delete', @el ).click( @delete_event )


    class NewStudyModal extends Backbone.Modal
        template: _.template( $( '#new-study-template' ).html() )
        submitEl: '.btn-primary'
        cancelEl: '.btn-cancel'

        clean: () ->
            values =
                name: $( '#study-name' ).val().replace( /^\s+|\s+$/g, "" )
                description: $( '#study-description' ).val().replace( /^\s+|\s+$/g, "" )
                tracker: $( '#study-tracker' ).is( ':checked' )

            return values

        beforeSubmit: () ->

            @cleaned_data = @clean()

            if @cleaned_data[ 'name' ].length == 0
                $( '.error', $( '#study-name' ).parent() ).html( 'Please used a valid study name' )
                return false

        submit: () ->
            study = new StudyModel()
            study.save( @cleaned_data,
                headers: {'X-CSRFToken': $.cookie( 'csrftoken' )}
                success: ( model, response, options )=>
                    model.set( {id: response.id} )
                    @collection.add( model )
                    )

    class DashboardView extends Backbone.View
        el: $( '#dashboard' )

        filter: 'all'

        repo_list: $( '#repo_list > tbody' )
        study_list: $( '#study_list' )

        events:
            "click #studies .create-new a":     "new_study_event"
            "click .study-settings a":          "study_settings_event"

            "click #filters li a":              "filter_repos_event"
            "click #studies ul li a":           "refresh_repos_event"

        filter_repos_event: (event) ->
            $( '.selected', '#filters' ).removeClass( 'selected' )
            $( event.currentTarget ).parent().addClass( 'selected' )

            @repo_view.filter( $( event.currentTarget ).data( 'filter' ) )

        new_study_event: (event) ->
            @modalView = new NewStudyModal( { collection: @study_view.collection } )
            $('.modal').html( @modalView.render().el )
            $( '#study-name' ).focus()

        study_settings_event: (event) ->
            event.stopImmediatePropagation()

            # Grab the study that this is for.
            study = new StudyModel(
                            id: $( event.currentTarget ).data( 'id' )
                            name: $( event.currentTarget ).data( 'name' )
                            )

            # Create the modal and display it!
            @modalView = new StudySettingsModal(
                                'collection': @study_view.collection
                                'study': study )
            $('.modal').html( @modalView.render().el )

        initialize: ->
            # Initialize our collections!
            @repo_view = new RepoCollectionView()
            @study_view = new StudyCollectionView()

        refresh_repos_event: (event) ->
            # Update the "Study" name and highlight the one the user just clicked.
            $( '#study_name' ).html( $( event.currentTarget ).html()  )
            $( '#studies .selected' ).removeClass( 'selected' )
            $( event.currentTarget ).parent().addClass( 'selected' )

            # Fetch the new set of repositories
            @repo_view.refresh( $( event.currentTarget ).data( 'study' ) )

            @

    return DashboardView
)