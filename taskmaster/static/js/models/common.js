define([
  'backbone'
], function(Backbone) {

  var Common = Backbone.Model.extend({
    sync: function() {},
    fetch: function() {
      this.set({
        permissionLevels: STATE.all_levels
      });
    }
  });

  return Common;
});
