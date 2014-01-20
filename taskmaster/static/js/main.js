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

$(function() {
    $('.delete-queue').click(function() {
        var id = $(this).data('id')
        $.ajax({
            url: '/queue/' + id,
            type: 'DELETE',
            success: removeQueue
        });
    function removeQueue(result) {
        $('#' + id).remove();
    }
    });
});

$(function () {
    $('#create-queue').click(function(){
        createQueue($('#queue-name').val());
    });
});

$('#queue-name').keyup(function(ev) {
    if (ev.which == 13) {
        createQueue($('#queue-name').val());
    }   
});

function createQueue(queue) {
    $.ajax({
          url: '/queue/' + queue,
          type: 'POST',
          success: addQueue
        });  
    function addQueue(result) {
       $('#queue-list').append('<li id=' + queue + '><a href="#" class="delete-queue" data-id=' + queue + '>x</a> ' + queue +'</li>');
    }
};


$(function() {
    $('#task-status').change(function() {
        var status = $('#task-status').val();
        var taskId = $('#task-status').data('task-id');
        $.ajax({
          url: '/task/' + taskId  + '/update/' + 'status/' + status,
          type: 'POST'
        });
    });
});

