$(document).ready(function () {
    // ──────────────────────────────────────────────────────────
    // Summernote 초기화 (글쓰기 & 수정 페이지 공통)
    // ──────────────────────────────────────────────────────────
    if ($('#summernote').length) {
      $('#summernote').summernote({
        height: 300,
        placeholder: '내용을 작성하세요.',
        tabsize: 2,
        callbacks: {
          onImageUpload: function (files) {
            const formData = new FormData();
            formData.append('file', files[0]);
  
            $.ajax({
              url: '/board/upload_image',
              method: 'POST',
              data: formData,
              processData: false,
              contentType: false,
              success: function (response) {
                $('#summernote').summernote('insertImage', response.url);
              },
              error: function () {
                alert('이미지 업로드 실패');
              }
            });
          }
        }
      });
    }
  
    // ──────────────────────────────────────────────────────────
    // 글쓰기 폼 제출 (AJAX)
    // ──────────────────────────────────────────────────────────
    $('#post-form').on('submit', function (e) {
      e.preventDefault();
  
      const title = $('input[name="title"]').val().trim();
      const content = $('#summernote').summernote('code').trim();
  
      if (!title || !content) {
        alert('제목과 내용을 모두 입력해주세요.');
        return;
      }
  
      $.ajax({
        type: 'POST',
        url: '/board/write',
        contentType: 'application/json',
        data: JSON.stringify({ title, content }),
        success: function (response) {
          alert(response.message);
          window.location.href = '/board';
        },
        error: function () {
          alert('글 작성 중 오류가 발생했습니다.');
        }
      });
    });
  
    // ──────────────────────────────────────────────────────────
    // 수정 폼 제출 (AJAX)
    // ──────────────────────────────────────────────────────────
    $('#edit-form').on('submit', function (e) {
      e.preventDefault();
  
      const title = $('#title').val().trim();
      const content = $('#summernote').summernote('code').trim();
  
      if (!title || !content) {
        alert('제목과 내용을 모두 입력해주세요.');
        return;
      }
  
      // URL에서 post_id 추출 (경로 예: /board/123/edit)
      const pathParts = window.location.pathname.split('/');
      const postId = pathParts[pathParts.length - 2];
  
      $.ajax({
        type: 'POST',
        url: `/board/${postId}/edit`,
        contentType: 'application/json',
        data: JSON.stringify({ title, content }),
        success: function (response) {
          alert(response.message);
          window.location.href = `/board/${postId}`;
        },
        error: function () {
          alert('수정 중 오류가 발생했습니다.');
        }
      });
    });
  
    // ──────────────────────────────────────────────────────────
    // 삭제 버튼 클릭 시 AJAX 요청 (상세보기 페이지 전용)
    // ──────────────────────────────────────────────────────────
    const deleteBtn = document.getElementById('delete-btn');
    if (deleteBtn) {
      deleteBtn.addEventListener('click', function () {
        if (!confirm("정말 삭제하시겠습니까?")) return;
  
        // 상세보기 버튼에 data-post-id 속성을 붙였으므로 여기서 꺼냄
        const postId = deleteBtn.getAttribute('data-post-id');
  
        $.ajax({
          type: 'POST',
          url: `/board/${postId}/delete`,
          contentType: 'application/json',
          success: function (response) {
            alert(response.message);
            history.back()
          },
          error: function () {
            alert('삭제 중 오류가 발생했습니다.');
          }
        });
      });
    }
  });
  
  // ──────────────────────────────────────────────────────────
  // 목록에서 상세 페이지로 이동시키는 함수
  // (board_list.html의 onclick="detail({{ post.id }})" 호출용)
  // ──────────────────────────────────────────────────────────
  function detail(postId) {
    window.location.href = `/board/${postId}`;
  }
  