define([
  'underscore',
  'backbone'
], function(_, Backbone) {

  var CurrentUser = Backbone.Model.extend({
    sync: function() {},
    fetch: function() {
      this.set({
        permissions: STATE.user.permissions,
        lteRoles: STATE.user.lte_roles,
      });
    }
  });

  return CurrentUser;
});
