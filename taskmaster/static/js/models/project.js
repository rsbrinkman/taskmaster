define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone) {

  var Project = Backbone.Model.extend({
    sync: function() {},
    fetch: function() {
      this.set({
        id: STATE.org.id,
        name: STATE.org.name,
        level: STATE.org.level,
        pendingInvites: STATE.pending_invites
      });
    },

    inviteUser: function(email, role) {
      $.ajax({
        type: 'POST',
        url: '/org/' + this.get('id') + '/user/' + email + '/',
        data: {
          role: role
        },
        success: function() {
          var invites = _.clone(this.get('pendingInvites'));

          invites.push({
            email: email,
            role: role
          });

          this.set('pendingInvites', invites);
        }.bind(this)
      });
    },

    cancelInvite: function(email) {
      $.ajax({
        type: 'DELETE',
        url: '/org/' + this.get('id') + '/user/' + email + '/',
        success: function() {
          var invites = _.reject(this.get('pendingInvites'), function(invite) {
            return invite.email === email;
          });

          this.set('pendingInvites', invites);
        }.bind(this)
      });
    },

    update: function(attr, value) {
      $.ajax({
        type: 'PUT',
        url: '/org/' + this.get('id') + '/' + attr,
        data: {
          value: value
        },
        success: function() {
          this.set(attr, value)
        }.bind(this)
      });
    }
  });

  return Project;
});
