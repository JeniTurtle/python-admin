$(function() {
    var item_count = $('.verify-list-item').length,
        num = 0;

    $('.verify-select').on('change', function() {
        var val = $(this).val();
        if (val != 1 && val != 2 && val != 3) {
            return false;
        }

        if(!window.confirm('你确定要评审该作品吗？评审后将无法再次修改')){
            $(this).find("option[value='0']").attr("selected",true);
            return false;
        }

        var ipId = $(this).attr('data-ipId');
        var verifyType = $(this).attr('data-verifyType');
        var $that = $(this).parent().parent();

        $.ajax({
            type: "GET",
            url: "/sampling/api/verify",
            data: {
                objectId: ipId,
                verifyType: verifyType,
                verifyResult: val
            },
            dataType: "json",
            success: function(data){
                if (data.error) {
                    alert(data.message);
                    return;
                }
                if (data.verifyResult == '0') {
                    alert('天啊！你都做了什么？');
                    return false;
                } else {
                    alert('评审成功！');
                    $that.find('.operation-td').html('无法操作');

                    if (data.verifyResult == '1') {
                        if (verifyType == 1) {
                            $that.find('.ippool-status').show().removeClass('text-danger').addClass('text-navy').text('一评通过');
                        } else if (verifyType == 3) {
                            $that.find('.ippool-status').show().removeClass('text-danger').addClass('text-navy').text('二评通过');
                        } else if (verifyType == 4) {
                            $that.find('.ippool-status').show().removeClass('text-danger').addClass('text-navy').text('二评复审通过');
                        }

                        $that.find('.verify-result').removeClass('text-warning').addClass('text-navy').text('抽检通过')
                    } else if (data.verifyResult == '2') {
                        if (verifyType == 1) {
                            $that.find('.ippool-status').show().removeClass('text-navy').addClass('text-warning').text('一评不通过');
                        } else if (verifyType == 3) {
                            $that.find('.ippool-status').show().removeClass('text-navy').addClass('text-warning').text('二评不通过');
                        } else if (verifyType == 4) {
                            $that.find('.ippool-status').show().removeClass('text-navy').addClass('text-warning').text('二评复审不通过');
                        }
                        $that.find('.verify-result').removeClass('text-warning').addClass('text-danger').text('抽检不通过')
                    } else if (data.verifyResult == '3') {
                        $that.find('.verify-result').removeClass('text-warning').text('放弃')
                    }

                    $that.find('.ippool-hide').hide()

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