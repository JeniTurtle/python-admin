$(function() {
    var $layer = $('.checkResult');

    $('.check-detail-btn').on('click', function() {
        var ipId = $(this).data('ipid');
        var title = $(this).data('title');
        $layer.find('h3').text("投票详情（" + title + "）");
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
                    var $p = $('<p>'+item.voterName+'</p>')
                    var $span = $('<span style="padding-left: 12px"></span>')
                    if (item.result == 1) {
                        $span.text('推荐');
                        $span.addClass('text-navy');
                    } else if (item.result == 2) {
                        $span.text('不推荐');
                        $span.addClass('text-danger');
                    } else {
                        $span.text('错误状态');
                        $span.addClass('text-warning');
                    }
                    $p.append($span).append('<span style="padding-left: 12px">'+item.createAt+'</span>');
                    $layer.find('.verify-list').append($p);
                }

                for (var index in data.overplus) {
                    var item = data.overplus[index];
                    var $p = $('<p>'+item.name+'</p>')
                    var $span = $('<span class="text-warning" style="padding-left: 12px">未投票</span>')
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

    $('.pass-btn').on('click', function() {
        if(!window.confirm('确定将此作品设为黑名单吗？确认后将无法修改！')){
            return false;
        }
        var ipId = $(this).data('ipid');

        $.ajax({
            type: "POST",
            url: "/blacklist/joinBlacklist/api",
            data: {
                ipId: ipId
            },
            dataType: "json",
            success: function(data){
                if (!data.error) {
                    alert('操作成功！');
                    window.location.reload();
                } else if (data.error == 202) {
                    alert('无权限操作！');
                } else if (data.error == 203) {
                    alert('该作品未进入候选池或已进入黑名单！');
                } else {
                    alert('数据请求失败，请重新刷新页面！');
                }
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    });
});