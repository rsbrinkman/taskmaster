define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/user_projects.html',
  'click_to_edit'
], function($, _, Backbone, UserProjectsTemplate) {

  var UserProjectsView = Backbone.View.extend({
    template: _.template(UserProjectsTemplate),
    events: {
      'click .go-settings': goSettings,
      'click .go-tasks': goTasks,
      'click #find-more': findMore,
      'submit #create-project': createProject
    },

    initialize: function(options) {
      this.appState = options.appState;
      this.currentUser = this.appState.currentUser;
    },

    render: function() {
      this.$el.html(this.template({
        currentUser: this.currentUser.toJSON()
      }));

      return this;
    },

    createProject: function(event) {
      event.stopPropagation();
      event.preventDefault();

      var name = this.$('#create-project-name').val();

      console.log('create project: ' + name);
    },

    findMore: function() {

    },

    goSettings: function(event) {
      var projectId = $(event.target).parents('tr').data('project-id');
    },

    goTasks: function(event) {
      var projectId = $(event.target).parents('tr').data('project-id');


    }

  });

  return UserProjectsView;
});
