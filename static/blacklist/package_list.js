$(function() {
    var $layer = $('.checkResult');

    $('.reason-detail-btn').on('click', function() {
        var ipId = $(this).data('ipid');
        var title = $(this).data('title');
        $layer.find('h3').text(title);
        $layer.find('.verify-list').html('');

        $.ajax({
            type: "GET",
            url: "/blacklist/voteDetail/api",
            data: {
                ipId: ipId
            },
            dataType: "json",
            success: function(data){
                if (data.error) {
                    alert('数据请求失败，请重新刷新页面！');
                    return;
                }

                $layer.show();

                for (var index in data.voteList) {
                    var item = data.voteList[index];

                    if (item.result != 1) {
                        continue;
                    }

                    var $p = $('<p>'+item.voterName+'：</p>')
                    var $span = $('<span class="text-navy" style="padding-left: 12px">'+item.reason+'</span>')

                    $p.append($span);
                    $layer.find('.verify-list').append($p);
                }

                var marginTop = ($(window).height() - $('.modal-dialog').height()) / 2;
                $('.modal-dialog').css({
                    'margin-top': marginTop
                });
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    });
});