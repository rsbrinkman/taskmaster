$(function() {
  $('.task-tags').select2({
    placeholder: "Add a tag",
    tags: TAGS.split(',')
  }).change(function(val) {
    $.ajax({
      url: '/task/' + $(this).data('tag-id') + '/tags/',
      type: 'POST',
      data: {
        tags: JSON.stringify(val.val)
      }
    });
  });

  $('.del-task').on('click', function() {
    var $cell = $(this);
    $.ajax({
      url: '/task/' + $cell.data('task-id'),
      type: 'DELETE',
      success: function() {
        $cell.parents('.task-row').remove();
        if (!$('.task-row').length) {
          $('#no-task-message').show();
        }
      }
    });
  });
});
