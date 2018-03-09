$(function() {

    var $layer = $('.checkResult');

    function submitForm(pass, reason) {
        var checkApi = $('#check-api').text();
        var copyId = $('#copy-id').text();
        var token = $('#leancloud-token').text();

        $.ajax({
            type: "GET",
            url: checkApi,
            data: {
                copyId: copyId,
                pass: pass,
                reason: reason || '审核通过',
                token: token
            },
            dataType: "jsonp",
            success: function(data){

                if (data.errno != 0) {
                    alert('数据请求失败，请重新刷新页面！');
                    return;
                }
                if (pass >= 1) {
                    alert('已通过审核！');
                } else {
                    alert('已驳回审核！');
                }
            },
            error: function() {
                alert('数据加载失败，请重新刷新页面！');
            }
        });
    }

    $('#workcheck-pass').on("click", function() {
        if(!window.confirm('你确定要通过此版保审核吗？')){
            return false;
        }
        submitForm(1);
    });

    $('#workcheck-refuse').on("click", function() {

        $layer.find('#pass-reason').val('');
        $layer.show();
    });

    $('#reason-btn').on('click', function() {
        var reason = $layer.find('#pass-reason').val();

        if (!reason) {
            alert("驳回原因不能为空！");
            return false;
        }

        if(!window.confirm('你确定要驳回此版保审核吗？')){
            return false;
        }

        submitForm(0, reason);

        $layer.hide();
    });
});