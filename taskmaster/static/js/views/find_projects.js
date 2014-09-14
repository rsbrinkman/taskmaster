define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/find_projects.html',
  'click_to_edit'
], function($, _, Backbone, FindProjectsTemplate) {

  var FindProjectsView = Backbone.View.extend({
    template: _.template(FindProjectsTemplate),
    events: {
    },

    initialize: function(options) {
      this.appState = options.appState;
      this.currentUser = this.appState.currentUser;
      this.currentProject = this.appState.currentProject;
      this.common = this.appState.common;
    },

    render: function() {
      this.$el.html(this.template({
        STATE: STATE,
        currentProject: this.currentProject.toJSON(),
        currentUser: this.currentUser.toJSON()
      }));

      return this;
    }

  });

  return FindProjectsView;
});
