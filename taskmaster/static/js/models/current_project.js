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
        pendingInvites: STATE.pending_invites
      });
    }
  });

  return Project;
});
