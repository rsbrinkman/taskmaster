define([
  'jquery',
  'underscore',
  'backbone',
  'text!templates/_project_users.html',
  'click_to_edit'
], function($, _, Backbone, ProjectUsersTemplate) {

  var ProjectUsersView = Backbone.View.extend({
    template: _.template(ProjectUsersTemplate),
    events: {
      'submit .invite-user': 'inviteUser',
      'click .cancel-invite': 'cancelInvite',
      'click .kick-user': 'kickUser'
    },

    initialize: function(options) {
      this.appState = options.appState;
      this.currentUser = this.appState.currentUser;
      this.currentProject = this.appState.currentProject;
      this.currentProjectUsers = this.appState.currentProjectUsers;

      this.listenTo(this.currentProject, 'change:pendingInvites', this.render);
      this.listenTo(this.currentProjectUsers, 'add remove', this.render);
    },

    render: function() {
      this.$el.html(this.template({
        projectUsers: this.currentProjectUsers.toJSON(),
        currentProject: this.currentProject.toJSON(),
        currentUser: this.currentUser.toJSON()
      }));

      this.$('.user-role-container.permitted').clickToEdit({
        inputType: 'select',
        choices: this.currentUser.get('lteRoles'),
        success: function($editable) {
          var userId = $editable.parents('tr').data('user-id'),
              role = $editable.val();

          this.currentProjectUsers.updateRole(userId, role);
        }.bind(this)
      });

      return this;
    },

    inviteUser: function(event) {
      event.stopPropagation();
      event.preventDefault();

      var email = $('.invite-user-email').val(),
          role = $('.invite-user-role').val();

      this.currentProject.inviteUser(email, role);
    },

    cancelInvite: function(event) {
      var email = $(event.target).parents('tr').find('.pending-email').text();
      this.currentProject.cancelInvite(email);
    },

    kickUser: function(event) {
      var userId = $(event.target).parents('tr').data('user-id');
      this.currentProjectUsers.kick(userId);
    }

  });

  return ProjectUsersView;
});
