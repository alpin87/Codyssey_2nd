# todo.py

from fastapi import FastAPI, APIRouter, HTTPException
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
import csv
import os

# 1. model.py에서 TodoItem 모델을 가져옵니다.
try:
    from model import TodoItem
except ImportError:
    print('---' * 10)
    print('오류: model.py 파일이 없거나 TodoItem 클래스를 찾을 수 없습니다.')
    print('---' * 10)
    exit() # 모델 없이는 실행 중단

# 전역 todo_list
todo_list: List[Dict] = []

# CSV 파일 경로
CSV_FILE = 'todo_data.csv'
# 2. (수정) CSV 파일 헤더에 'id'를 포함하여 고정합니다.
CSV_FIELDNAMES = ['id', 'title', 'description', 'completed']


def load_todos_from_csv():
    '''
    CSV 파일에서 TODO 데이터를 로드.
    (ID를 int로, completed를 bool로 변환하는 기능 포함)
    '''
    global todo_list
    if os.path.exists(CSV_FILE):
        temp_list = []
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # (중요!) ID를 정수(int)로, completed를 불리언(bool)으로 변환
                        row['id'] = int(row['id'])
                        row['completed'] = row['completed'].lower() == 'true'
                        temp_list.append(row)
                    except (KeyError, ValueError, TypeError):
                        print(f'경고: 유효하지 않은 행을 건너뜁니다: {row}')
            todo_list = temp_list
        except Exception as e:
            print(f'CSV 로드 중 오류 발생: {e}')
            todo_list = []
    else:
        # 파일이 없으면 빈 리스트로 시작
        todo_list = []


def save_todos_to_csv():
    '''
    TODO 데이터를 CSV 파일에 저장.
    (고정된 CSV_FIELDNAMES 사용)
    '''
    try:
        with open(CSV_FILE, 'w', encoding='utf-8', newline='') as file:
            # 3. (수정) fieldnames를 고정된 값으로 사용
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()
            if todo_list:
                writer.writerows(todo_list)
    except Exception as e:
        print(f'CSV 저장 중 오류 발생: {e}')


# 4. (추가) ID 생성을 위한 헬퍼 함수
def get_next_id() -> int:
    '''새로운 TODO 항목의 ID를 생성 (max(id) + 1)'''
    if not todo_list:
        return 1
    # 'id' 키가 없는 경우 0을 반환하여 max() 오류 방지
    return max(int(item.get('id', 0)) for item in todo_list) + 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''애플리케이션 생명주기 관리'''
    # 시작 시 실행
    load_todos_from_csv()
    print('FastAPI TODO 애플리케이션이 시작되었습니다.')
    print(f'기존 TODO 항목 {len(todo_list)}개를 로드했습니다.')
    yield
    # 종료 시 실행
    print('애플리케이션이 종료됩니다.')


app = FastAPI(lifespan=lifespan)
router = APIRouter()


@router.post('/add_todo')
async def add_todo(todo_item: TodoItem) -> Dict:
    '''
    새로운 TODO 항목을 추가하는 POST 엔드포인트
    (Dict 대신 TodoItem 모델 사용, ID 자동 생성)
    '''
    # Pydantic 모델을 딕셔너리로 변환
    new_todo_data = todo_item.model_dump()
    
    # 5. (수정) 새 ID 생성 및 추가
    new_todo_data['id'] = get_next_id()
    
    # todo_list에 항목 추가
    todo_list.append(new_todo_data)
    
    # CSV 파일에 저장
    save_todos_to_csv()
    
    return {
        'status': 'success',
        'message': 'TODO 항목이 추가되었습니다.',
        'data': new_todo_data  # 이제 new_todo_data에 id가 포함됨
    }


@router.get('/retrieve_todo')
async def retrieve_todo() -> Dict:
    '''
    전체 TODO 리스트를 가져오는 GET 엔드포인트 (기존 코드)
    '''
    return {
        'status': 'success',
        'count': len(todo_list),
        'data': todo_list
    }


# --- (요청) 신규 추가된 기능: 개별 조회 ---
@router.get('/todo/{todo_id}')
async def get_single_todo(todo_id: int) -> Dict:
    '''
    특정 ID의 TODO 항목을 가져오는 GET 엔드포인트
    '''
    for item in todo_list:
        if item.get('id') == todo_id: # ID (int) 비교
            return {
                'status': 'success',
                'data': item
            }
    
    raise HTTPException(
        status_code=404,
        detail=f'ID {todo_id}에 해당하는 TODO 항목을 찾을 수 없습니다.'
    )


# --- (요청) 신규 추가된 기능: 수정 ---
@router.put('/todo/{todo_id}')
async def update_todo(todo_id: int, todo_update: TodoItem) -> Dict:
    '''
    특정 ID의 TODO 항목을 수정하는 PUT 엔드포인트
    '''
    for i, item in enumerate(todo_list):
        if item.get('id') == todo_id: # ID (int) 비교
            updated_data = todo_update.model_dump()
            updated_data['id'] = todo_id # ID 유지
            
            todo_list[i] = updated_data
            save_todos_to_csv()
            
            return {
                'status': 'success',
                'message': 'TODO 항목이 수정되었습니다.',
                'data': updated_data
            }
            
    raise HTTPException(
        status_code=404,
        detail=f'ID {todo_id}에 해당하는 TODO 항목을 찾을 수 없습니다.'
    )


# --- (요청) 신규 추가된 기능: 삭제 ---
@router.delete('/todo/{todo_id}')
async def delete_single_todo(todo_id: int) -> Dict:
    '''
    특정 ID의 TODO 항목을 삭제하는 DELETE 엔드포인트
    '''
    item_found = False
    for i, item in enumerate(todo_list):
        if item.get('id') == todo_id: # ID (int) 비교
            del todo_list[i]
            item_found = True
            break
            
    if not item_found:
        raise HTTPException(
            status_code=404,
            detail=f'ID {todo_id}에 해당하는 TODO 항목을 찾을 수 없습니다.'
        )
        
    save_todos_to_csv()
    
    return {
        'status': 'success',
        'message': f'ID {todo_id}의 TODO 항목이 삭제되었습니다.'
    }
# --- ---


# 라우터를 앱에 등록
app.include_router(router)


if __name__ == '__main__':
    try:
        import uvicorn
        # 개발 편의를 위해 --reload 옵션을 활성화합니다.
        uvicorn.run('todo:app', host='0.0.0.0', port=8000, reload=True)
    except ImportError:
        print('Error: uvicorn이 설치되어 있지 않습니다.')
        print('  pip install uvicorn')
        print('  uvicorn todo:app --reload')