$(function() {
    var $layer = $('.checkResult');

    $(".allot-btn").on("click", function() {
        var ipId = $(this).data('ipid');
        $("#form-ipId").val(ipId);

        $("#packager .nullData").remove();
        $("#packager option").attr('disabled', 'disabled').removeClass('option-show').addClass('option-hide').removeAttr('selected');

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

                passNum = 0
                for (var index in data.voteList) {
                    if (data.voteList[index]['result'] == 1) {
                        passNum += 1;

                        $('#packager option').each(function() {
                            if ($(this).val() == data.voteList[index]['voterId']) {
                                $(this).removeAttr('disabled').removeClass('option-hide').addClass('option-show');
                            }
                        });
                    }
                }

                if (passNum == 0) {
                    $("#packager").prepend('<option class="option-show nullData">暂无包装人（无人推荐该作品）</option>');
                }

                $temp = $("#packager .option-show").first().attr('selected', 'selected').remove();
                $('#packager').prepend($temp);

                $layer.show();
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    });

    $('#package-btn').on('click', function() {
        var ipId = $("#form-ipId").val();
        var packagerId = $('#packager').find("option:selected").val();
        var uptime = $('#package-date-input').val();
        uptime = Date.parse(new Date(uptime)) / 1000;

        if (!packagerId) {
            alert('请选择包装人！');
            return false;
        }

        if(!window.confirm('确定要分配此作品吗？')){
            return false;
        }

        if (!ipId || !packagerId || !uptime) {
            alert('错误参数！');
            return false;
        }

        $.ajax({
            type: "POST",
            url: "/blacklist/blacklistPackage/api",
            data: {
                ipId: ipId,
                packagerId: packagerId,
                uptime: uptime
            },
            dataType: "json",
            success: function(data){
                if (!data.error) {
                    alert('操作成功！');
                    window.location.reload();
                } else if (data.error == 202) {
                    alert('无法重复分配包装人！');
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