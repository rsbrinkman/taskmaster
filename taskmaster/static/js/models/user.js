define([
  'underscore',
  'backbone'
], function(_, Backbone) {

  var CurrentUser = Backbone.Model.extend({
    sync: function() {},
    fetch: function() {
      this.set({
        id: STATE.user.id,
        role: STATE.user.role,
        permissions: STATE.user.permissions,
        lteRoles: STATE.user.lte_roles,
      });
    }
  });

  return CurrentUser;
});
