from fastapi import FastAPI, APIRouter, HTTPException
from typing import Dict
from contextlib import asynccontextmanager
import csv
import os

# 전역 todo_list
todo_list = []

# CSV 파일 경로
CSV_FILE = 'todo_data.csv'


def load_todos_from_csv():
    '''CSV 파일에서 TODO 데이터를 로드'''
    global todo_list
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            todo_list = [row for row in reader]


def save_todos_to_csv():
    '''TODO 데이터를 CSV 파일에 저장'''
    if todo_list:
        with open(CSV_FILE, 'w', encoding='utf-8', newline='') as file:
            fieldnames = todo_list[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(todo_list)


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''애플리케이션 생명주기 관리'''
    # 시작 시 실행
    load_todos_from_csv()
    print('FastAPI TODO 애플리케이션이 시작되었습니다.')
    print(f'기존 TODO 항목 {len(todo_list)}개를 로드했습니다.')
    yield
    # 종료 시 실행 (필요시)
    print('애플리케이션이 종료됩니다.')


app = FastAPI(lifespan=lifespan)
router = APIRouter()


@router.post('/add_todo')
async def add_todo(todo_item: Dict) -> Dict:
    '''
    새로운 TODO 항목을 추가하는 POST 엔드포인트
    
    Args:
        todo_item: TODO 항목을 담은 딕셔너리
        
    Returns:
        작업 결과를 담은 딕셔너리
    '''
    # 빈 값 체크 (보너스 과제)
    if not todo_item:
        raise HTTPException(
            status_code=400,
            detail='TODO 항목이 비어있습니다. 데이터를 입력해주세요.'
        )
    
    # todo_list에 항목 추가
    todo_list.append(todo_item)
    
    # CSV 파일에 저장
    save_todos_to_csv()
    
    return {
        'status': 'success',
        'message': 'TODO 항목이 추가되었습니다.',
        'data': todo_item
    }


@router.get('/retrieve_todo')
async def retrieve_todo() -> Dict:
    '''
    전체 TODO 리스트를 가져오는 GET 엔드포인트
    
    Returns:
        TODO 리스트를 담은 딕셔너리
    '''
    return {
        'status': 'success',
        'count': len(todo_list),
        'data': todo_list
    }


# 라우터를 앱에 등록
app.include_router(router)


if __name__ == '__main__':
    try:
        import uvicorn
        uvicorn.run(app, host='0.0.0.0', port=8000)
    except ImportError:
        print('Error: uvicorn이 설치되어 있지 않습니다.')
        print('다음 명령어로 설치해주세요:')
        print('  pip install uvicorn')
        print('\n또는 다음 명령어로 직접 실행하세요:')
        print('  uvicorn todo:app --reload')