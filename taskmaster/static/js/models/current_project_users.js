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
    sync: function() {},
    fetch: function() {
      _.each(STATE.users, function(user) {
        this.create({
          id: user.id,
          name: user.name,
          role: user.role
        });
      }.bind(this));
    }
  });

  return ProjectUsers;
});
