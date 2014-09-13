define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/project_settings.html',
  'click_to_edit'
], function($, _, Backbone, ProjectSettingsTemplate) {

  var ProjectSettingsView = Backbone.View.extend({
    template: _.template(ProjectSettingsTemplate),
    events: {
      'click #confirm-project-leave': 'leaveProject',
      'click #confirm-project-delete': 'deleteProject'
    },

    initialize: function(options) {
      this.appState = options.appState;
      this.currentUser = this.appState.currentUser;
      this.currentProject = this.appState.currentProject;
      this.common = this.appState.common;

      this.listenTo(this.currentProject, 'change:level', this.render);
    },

    leaveProject: function() {
      $.ajax({
        type: 'DELETE',
        url: '/org/' + this.currentProject.get('id') + '/user/' + this.currentUser.get('id') + '/',
        success: function() {
          window.location = "/admin";
        }
      });
    },

    deleteProject: function() {
      $.ajax({
        type: 'DELETE',
        url: '/org/' + this.currentProject.get('id'),
        success: function() {
          window.location = "/admin";
        }
      });
    },

    render: function() {
      this.$el.html(this.template({
        currentProject: this.currentProject.toJSON(),
        currentUser: this.currentUser.toJSON()
      }));

      this.$('.project-settings-name.permitted').clickToEdit({
        inputType: 'text',
        displayElement: 'h3',
        success: function($editable) {
          this.currentProject.update('name', $editable.val());
        }.bind(this)
      });

      this.$('.project-settings-level.permitted').clickToEdit({
        inputType: 'select',
        displayElement: 'strong',
        choices: this.common.get('permissionLevels'),
        success: function($editable) {
          this.currentProject.update('level', $editable.val());
        }.bind(this)
      });

      return this;
    }

  });

  return ProjectSettingsView;
});
