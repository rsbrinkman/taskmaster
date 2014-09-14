define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/user_settings.html',
  'click_to_edit'
], function($, _, Backbone, UserSettingsTemplate) {

  var UserSettingsView = Backbone.View.extend({
    template: _.template(UserSettingsTemplate),
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

  return UserSettingsView;
});
