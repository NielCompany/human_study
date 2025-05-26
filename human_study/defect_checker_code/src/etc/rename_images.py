import os

def rename_images(folder_path, prefix="image", start_num=1):
    # 1. 폴더 안의 모든 파일 목록 가져오기
    files = os.listdir(folder_path)
    # 2. 이미지 파일(.jpg, .jpeg, .png)만 필터링
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    start_num = 14233

    # 3. 이미지 파일 이름을 정렬 후 enumerate로 반복
    for idx, filename in enumerate(sorted(image_files), start=start_num):
        # 파일 확장자 추출 (.jpg 등), splitext 는 파일명을 " . " 을 기준으로 나눠주고 쩜도 포함해서 반환환
        ext = os.path.splitext(filename)[1].lower()

        # 새 이름 구성: 예) image00001.jpg
        new_name = f"{prefix}{idx:05d}{ext}"

        # 전체 경로 구성
        src = os.path.join(folder_path, filename)
        dst = os.path.join(folder_path, new_name)

        # 이름 변경 수행
        os.rename(src, dst)
        print(f"✅ {filename} → {new_name}")

if __name__ == "__main__":
    rename_images("data/samples3")