$(function() {
    var item_count = $('.verify-list-item').length,
        num = 0;

    $('.verify-select').on('change', function() {
        var val = $(this).val();
        if (val != 1 && val != 2) {
            return false;
        }

        if(!window.confirm('你确定要评审该作品吗？评审后将无法再次修改')){
            $(this).find("option[value='0']").attr("selected",true);
            return false;
        }

        var $that = $(this).parent().parent();
        var ipId = $(this).attr('data-ipId');
        var verifyType = $(this).attr('data-verifyType');

        $.ajax({
            type: "GET",
            url: "/ipverify/api/verify",
            data: {
                objectId: ipId,
                verifyType: verifyType,
                verifyResult: val
            },
            dataType: "json",
            success: function(data){
                if (data.error) {
                    alert('数据请求失败，请重新刷新页面！');
                    return;
                }
                if (data.verifyResult == '0') {
                    alert('天啊！你都做了什么？');
                    return false;
                } else {
                    alert('评审成功！');
                    $that.find('.operation-td').html('无法操作');

                    if (data.verifyResult == '1') {
                        $that.find('.verify-result').removeClass('text-warning').addClass('text-navy').text('通过')
                    } else if (data.verifyResult == '2') {
                        $that.find('.verify-result').removeClass('text-warning').addClass('text-danger').text('不通过')
                    }
                    num += 1;

                    if (num >= item_count) {
                        window.location.reload();
                    }
                }
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    });
});