$(function() {
    $('#login-btn').on('click', function() {
        var phone = $('#phone').val();
        var password = $('#password').val();
        $.ajax({
            type: "GET",
            url: "/login/api",
            data: {
                phone: phone,
                password: password
            },
            dataType: "json",
            success: function(data){
                if (data.error == '103') {
                    alert('账号或密码错误！');
                } else if (data.error == '101') {
                    alert('暂无登录权限！');
                } else if (data.error) {
                    alert('登录失败，请联系管理员查看！')
                } else {
                    window.location.href = '/home'
                }
            }
        });
    });
});