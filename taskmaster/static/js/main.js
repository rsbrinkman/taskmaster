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

  $('.container').on('click', '.delete-queue', function() {
    var $this = $(this);
    var id = $(this).data('queue-id');
    $.ajax({
      url: '/queue/' + id,
      type: 'DELETE',
      success: function(data) {
        $this.parents('.queue-row').remove();
      }
    });
  });

  $('.container').on('click', '.queue-row', function(e) {
    if(e.target === this) {
      $(this).toggleClass('selected');
    }
  });

  $('#create-queue').click(function(){
      createQueue($('#queue-name').val());
  });

  $('#queue-name').keyup(function(ev) {
    if (ev.which === 13) {
      createQueue($('#queue-name').val());
    }
  });
});

function createQueue(queue) {
    $.ajax({
          url: '/queue/' + queue,
          type: 'POST',
          success: addQueue
        });
    function addQueue(result) {
       $('#queue-list').append('<li class="queue-row"><a href="#" class="delete-queue" data-queue-id=' + queue + '>x</a> ' + queue +'</li>');
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

