$(function() {
    if ($('.refuse-btn').length == 0) {
        $('.null-data').show();
    }

    var $layer = $('.checkResult');

    $('.refuse-btn').on('click', function() {
        if(!window.confirm('确定不推荐此作品吗？确认后将无法修改！')){
            return false;
        }
        var ipId = $(this).data('ipid');
        vote(ipId, 2);
    });

    $('.pass-btn').on('click', function() {
        var $layer = $('.checkResult');
        var ipId = $(this).data('ipid');
        $layer.find('#pass-ipid').val(ipId);
        $layer.find('#pass-reason').val('');
        $layer.show();
    });

    $('#reason-btn').on('click', function() {
        var reason = $layer.find('#pass-reason').val();
        var ipId = $layer.find('#pass-ipid').val();

        if (!reason) {
            alert("推荐原因不能为空！");
            return false;
        }

        if(!window.confirm('确定推荐此作品吗？确认后将无法修改！')){
            return false;
        }

        vote(ipId, 1, reason);
    });

    function vote(ipId, result, reason) {
        $.ajax({
            type: "POST",
            url: "/blacklist/vote/api",
            data: {
                ipId: ipId,
                result: result,
                reason: reason || ""
            },
            dataType: "json",
            success: function(data){
                if (!data.error) {
                    alert('操作成功！');
                    window.location.reload();
                } else if (data.error == 202) {
                    alert('无法重复投票！');
                } else {
                    alert('数据请求失败，请重新刷新页面！');
                }
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    }
})