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

    render: function() {
      this.$el.html(this.template({
        STATE: STATE
      }));

      this.$('.user-role-container.permitted').clickToEdit({
        inputType: 'select',
        choices: STATE.user.lte_roles,
        success: function($editable) {
          var userId = $editable.parents('tr').data('user-id'),
              role = $editable.val();

          this.updateRole(userId, role);
        }.bind(this)
      });

      return this;
    },

    updateRole: function(userId, role) {
      $.ajax({
        type: 'PUT',
        url: '/org/' + STATE.org.id + '/user/' + userId + '/role/' + role + '/',
        success: function() {
          window.location.reload();
        }
      });
    },

    inviteUser: function(event) {
      event.stopPropagation();
      event.preventDefault();

      var email = $('.invite-user-email').val(),
          role = $('.invite-user-role').val();

      $.ajax({
        type: 'POST',
        url: '/org/' + STATE.org.id + '/user/' + email + '/',
        data: {
          role: role
        },
        success: function() {
          window.location.reload();
        }
      });
    },

    cancelInvite: function(event) {
      var email = $(event.target).parents('tr').find('.pending-email').text();
      this.deleteUser(email);
    },

    kickUser: function(event) {
      var userId = $(event.target).parents('tr').data('user-id');
      this.deleteUser(userId);
    },

    deleteUser: function(username) {
      $.ajax({
        type: 'DELETE',
        url: '/org/' + STATE.org.id + '/user/' + username + '/',
        success: function() {
          window.location.reload();
        }
      });
    }
  });

  return ProjectUsersView;
});
