var TEMPLATES = {}

$(function() {
  // Load Templates
  _.each($('[type="underscore"]'), function(ele) {
    var $ele = $(ele);
    TEMPLATES[$ele.data('template-name')] = _.template($ele.html());
  });

  $('#logout').on('click', function(e) {
    e.preventDefault();
    e.stopPropagation();

    $.ajax({
      url: '/logout',
      type: 'POST'
    });

    window.location = "/signup";
  });
});
