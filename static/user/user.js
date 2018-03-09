function getQueryString(name)
{
     var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
     var r = window.location.search.substr(1).match(reg);
     if(r!=null)return  unescape(r[2]); return null;
}

$(function() {
    var crm = getQueryString('crm');
    if (!crm) {
        var str = $('.check-type').eq(0).addClass('active');
    } else {
        $('.check-type').each(function() {
            var str = $(this).attr('onclick');
            var index = str.indexOf(crm);
            if (index > -1) {
                $(this).addClass('active');
            }
        });
    }
    var mobile = getQueryString('mobile');
    if (mobile) {
        $('#mobile-input').val(mobile)
    }
});

function verifyDetail(uid) {
    $.ajax({
        type: "GET",
        url: "/home/api/verifycount",
        data: {
            uid: uid
        },
        dataType: "json",
        success: function(data){
            if (data.error) {
                alert('数据请求失败，请重新刷新页面！');
                return;
            }
            console.log(data);
            $('.checkResult').show();
            $('.modal-dialog').show();
            $p = $('.count-list').find('p');
            $p.eq(0).html('<span class="text-warning">待评审数量</span>：' + data.data.pendingCount)
            $p.eq(1).html('<span class="text-navy">已评审数量<span>：' + data.data.verifiedCount)
            $p.eq(2).html('<span class="text-warning">待抽检数量</span>：' + data.data.samplingPendingCount)
            $p.eq(3).html('<span class="text-navy">已抽检数量<span>：' + data.data.samplingVerifiedCount)
        },
        error: function() {
            alert('数据请求失败，请重新刷新页面！');
        }
    });
}