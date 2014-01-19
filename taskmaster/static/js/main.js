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
});

$(function() {
    $('.delete-queue').click(function() {
        var id = $('.delete-queue').data('id');
        $.ajax({
            url: '/queue/delete/' + id,
            type: 'POST',
            success: removeQueue
        });
    function removeQueue(result) {
        $('#' + id).remove();
    }
    });
});

$(function() {
    $('#task-status').change(function() {
        //Don't want to mix in vanilla js, couldn't get jquery .val() to work
        //alert(this.value);
        var status = $('#task-status').val();
        var taskId = $('#task-status').data('task-id');
        $.ajax({
          url: '/task/' + taskId  + '/update_status/' + status,
          type: 'POST'
        });
    });
});

