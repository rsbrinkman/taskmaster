define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone) {

  var ProjectUser = Backbone.Model.extend({
    sync: function() {}
  });

  var ProjectUsers = Backbone.Collection.extend({
    model: ProjectUser,
    initialize: function() {
      this.projectId = STATE.org.id;
    },
    sync: function() {},
    fetch: function() {
      _.each(STATE.users, function(user) {
        this.create({
          id: user.id,
          name: user.name,
          role: user.role
        });
      }.bind(this));
    },

    kick: function(userId) {
      $.ajax({
        type: 'DELETE',
        url: '/org/' + this.projectId + '/user/' + userId + '/',
        success: function() {
          this.findWhere({
            id: userId
          }).destroy();
        }.bind(this)
      });
    },

    updateRole: function(userId, role) {
      $.ajax({
        type: 'PUT',
        url: '/org/' + this.projectId + '/user/' + userId + '/role/' + role + '/',
        success: function() {
          var updatedUser = this.findWhere({
            id: userId
          });

          updatedUser.set('role', role);
        }.bind(this)
      });
    }
  });

  return ProjectUsers;
});
