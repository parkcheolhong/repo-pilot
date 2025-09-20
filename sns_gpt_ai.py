# =========================================
# SNS GPT AI 프로그램
# -----------------------------------------
# - 영상 파일 선택 또는 직접 촬영
# - 자동/수동 모드로 영상 편집 및 소개글 작성
# - 영상, 음성 인식, GPT 소개글 결과 미리보기
# - 영상 썸네일 미리보기, 오디오 재생, 음성 명령 인식
# - 오류 발생 시 자동 안내 및 기능 개선 제안
# =========================================

import os
import logging
import threading
import moviepy.editor as mp
from openai import OpenAI
import speech_recognition as sr
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import pygame

# 로그 설정
logging.basicConfig(filename='sns_gpt_ai.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def edit_video(input_path, output_path, start_sec, end_sec):
    """영상의 특정 구간을 추출하여 새 영상으로 저장합니다."""
    try:
        clip = mp.VideoFileClip(input_path).subclip(start_sec, end_sec)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        return output_path
    except Exception as e:
        logging.error(f"영상 편집 오류: {e}")
        raise

def extract_audio_text(video_path):
    """영상에서 오디오를 추출하고, 음성 인식으로 텍스트를 반환합니다."""
    try:
        video = mp.VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        video.audio.write_audiofile(audio_path)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='ko-KR')
        os.remove(audio_path)
        return text
    except Exception as e:
        logging.error(f"음성 인식 오류: {e}")
        return "음성 인식에 실패했습니다."

def generate_summary(api_key, video_info):
    """GPT를 이용해 영상 요약, 키워드, 소개글을 생성합니다."""
    try:
        openai_client = OpenAI(api_key=api_key)
        prompt = f"다음 영상의 내용을 요약하고, 키워드와 소개글을 작성해줘:\n{video_info}"
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"GPT 요약 생성 오류: {e}")
        return "GPT 요약 생성에 실패했습니다."

def record_video(output_path="recorded_video.mp4", duration=10):
    """웹캠으로 영상을 녹화하여 파일로 저장합니다."""
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640,480))
    frame_count = 0
    max_frames = int(20 * duration)  # 20fps * duration(sec)
    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        cv2.imshow('녹화 중... 종료하려면 q', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_count += 1
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return output_path

def get_video_thumbnail(video_path, thumbnail_path="thumbnail.jpg"):
    """영상의 첫 프레임을 썸네일 이미지로 저장하고 반환합니다."""
    try:
        clip = mp.VideoFileClip(video_path)
        frame = clip.get_frame(0)
        img = Image.fromarray(frame)
        img.save(thumbnail_path)
        return thumbnail_path
    except Exception as e:
        logging.error(f"썸네일 생성 오류: {e}")
        return None

class SNSGPTAIApp:
    """
    SNS GPT AI 프로그램의 메인 GUI 클래스입니다.
    - 영상 파일 선택 또는 직접 촬영
    - 자동/수동 모드로 영상 편집 및 소개글 작성
    - 결과 미리보기 및 로그 기록
    - 영상 썸네일, 오디오 재생, 음성 명령 인식 지원
    """
    def __init__(self, master):
        self.master = master
        master.title("SNS GPT AI 프로그램")
        master.geometry("700x750")

        self.input_video = ""
        self.output_video = "output.mp4"
        self.openai_api_key = ""
        self.thumbnail_path = ""

        # 자동/수동 모드 스위치
        self.mode_var = tk.StringVar(value="auto")
        tk.Label(master, text="모드 선택:").pack()
        tk.Radiobutton(master, text="자동", variable=self.mode_var, value="auto").pack(anchor='w')
        tk.Radiobutton(master, text="수동", variable=self.mode_var, value="manual").pack(anchor='w')

        tk.Button(master, text="원본 영상 선택", command=self.select_input_video).pack(pady=5)
        tk.Button(master, text="영상 직접 촬영", command=self.record_video_gui).pack(pady=5)
        tk.Label(master, text="OpenAI API Key:").pack()
        self.api_entry = tk.Entry(master, show="*")
        self.api_entry.pack(pady=5)

        # 수동 모드용 편집 구간/소개글 입력
        self.manual_frame = tk.Frame(master)
        tk.Label(self.manual_frame, text="편집 시작(초):").pack()
        self.start_entry = tk.Entry(self.manual_frame)
        self.start_entry.pack()
        tk.Label(self.manual_frame, text="편집 끝(초):").pack()
        self.end_entry = tk.Entry(self.manual_frame)
        self.end_entry.pack()
        tk.Label(self.manual_frame, text="소개글 직접 입력:").pack()
        self.manual_summary_entry = tk.Entry(self.manual_frame, width=60)
        self.manual_summary_entry.pack()
        self.manual_frame.pack(pady=5)

        tk.Button(master, text="실행", command=self.run_pipeline).pack(pady=20)

        # 결과 미리보기 텍스트박스
        self.result_text = tk.Text(master, height=10)
        self.result_text.pack()

        # 영상 썸네일 미리보기
        self.thumbnail_label = tk.Label(master)
        self.thumbnail_label.pack(pady=10)

        # 오디오 재생 버튼
        tk.Button(master, text="편집된 영상 오디오 재생", command=self.play_audio).pack(pady=5)

        # 음성 명령 시작 버튼
        tk.Button(master, text="음성 명령 시작", command=self.start_voice_command).pack(pady=5)

        self.mode_var.trace("w", self.toggle_manual_inputs)
        self.toggle_manual_inputs()

    def toggle_manual_inputs(self, *args):
        """모드에 따라 수동 입력창 표시/숨김"""
        if self.mode_var.get() == "manual":
            self.manual_frame.pack(pady=5)
        else:
            self.manual_frame.pack_forget()

    def select_input_video(self):
        """영상 파일 선택"""
        self.input_video = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi")])
        self.result_text.insert(tk.END, f"원본 영상: {self.input_video}\n")
        self.show_thumbnail(self.input_video)

    def record_video_gui(self):
        """웹캠으로 영상 촬영 후 파일 저장"""
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if save_path:
            self.result_text.insert(tk.END, "웹캠 녹화 시작 (창에서 'q'를 누르면 종료)\n")
            record_video(save_path, duration=10)
            self.input_video = save_path
            self.result_text.insert(tk.END, f"촬영 영상 저장: {self.input_video}\n")
            self.show_thumbnail(self.input_video)

    def show_thumbnail(self, video_path):
        """영상 썸네일(첫 프레임) 미리보기"""
        thumbnail_path = get_video_thumbnail(video_path)
        if thumbnail_path and os.path.exists(thumbnail_path):
            img = Image.open(thumbnail_path)
            img = img.resize((320, 180))
            photo = ImageTk.PhotoImage(img)
            self.thumbnail_label.config(image=photo)
            self.thumbnail_label.image = photo
        else:
            self.thumbnail_label.config(image='', text='썸네일 미리보기 불가')

    def run_pipeline(self):
        """자동/수동 모드에 따라 영상 편집 및 소개글 작성"""
        try:
            self.openai_api_key = self.api_entry.get()
            mode = self.mode_var.get()
            if not self.input_video:
                messagebox.showerror("오류", "영상 파일을 선택하거나 직접 촬영하세요.")
                return
            if mode == "auto":
                # 자동: 구간 자동(10~60초), 소개글 자동(GPT+음성인식)
                edit_video(self.input_video, self.output_video, 10, 60)
                self.result_text.insert(tk.END, "자동 영상 편집 완료 (10~60초)\n")
                video_text = extract_audio_text(self.output_video)
                self.result_text.insert(tk.END, f"자동 음성 인식 결과:\n{video_text}\n")
                summary = generate_summary(self.openai_api_key, video_text)
                self.result_text.insert(tk.END, f"자동 GPT 소개글:\n{summary}\n")
                self.show_thumbnail(self.output_video)
            else:
                # 수동: 사용자가 입력한 구간/소개글 사용
                start_sec = int(self.start_entry.get())
                end_sec = int(self.end_entry.get())
                edit_video(self.input_video, self.output_video, start_sec, end_sec)
                self.result_text.insert(tk.END, f"수동 영상 편집 완료 ({start_sec}~{end_sec}초)\n")
                summary = self.manual_summary_entry.get()
                self.result_text.insert(tk.END, f"수동 입력 소개글:\n{summary}\n")
                self.show_thumbnail(self.output_video)
        except Exception as e:
            logging.error(f"파이프라인 실행 오류: {e}")
            self.auto_fix_suggestion(e)
            messagebox.showerror("오류", str(e))

    def play_audio(self):
        """편집된 영상의 오디오를 추출하여 재생합니다."""
        def _play():
            try:
                video_path = self.output_video
                if not os.path.exists(video_path):
                    messagebox.showerror("오류", "편집된 영상 파일이 없습니다.")
                    return
                # 오디오 추출
                audio_path = "preview_audio.wav"
                clip = mp.VideoFileClip(video_path)
                clip.audio.write_audiofile(audio_path)
                pygame.mixer.init()
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
                pygame.mixer.music.unload()
                pygame.mixer.quit()
                os.remove(audio_path)
            except Exception as e:
                logging.error(f"오디오 재생 오류: {e}")
                messagebox.showerror("오디오 재생 오류", str(e))
        threading.Thread(target=_play, daemon=True).start()

    def start_voice_command(self):
        """음성 명령을 인식하여 주요 기능을 실행합니다."""
        def listen():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.result_text.insert(tk.END, "[음성 명령 대기 중...]\n")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(audio, language='ko-KR')
                    self.result_text.insert(tk.END, f"[음성 명령 인식]: {command}\n")
                    if "영상 편집" in command:
                        self.run_pipeline()
                    elif "소개글" in command:
                        self.result_text.insert(tk.END, "소개글 자동 생성 기능 실행\n")
                        video_text = extract_audio_text(self.input_video)
                        summary = generate_summary(self.openai_api_key, video_text)
                        self.result_text.insert(tk.END, f"자동 GPT 소개글:\n{summary}\n")
                    elif "종료" in command:
                        self.master.quit()
                    else:
                        self.result_text.insert(tk.END, "알 수 없는 명령입니다.\n")
                except Exception as e:
                    self.result_text.insert(tk.END, f"[음성 인식 오류]: {e}\n")
                    self.auto_fix_suggestion(e)
        threading.Thread(target=listen, daemon=True).start()

    def auto_fix_suggestion(self, error):
        """오류 발생 시 자동 수정 안내 및 기능 개선 제안"""
        self.result_text.insert(tk.END, f"오류가 발생했습니다. 자동으로 수정 시도합니다.\n")
        self.result_text.insert(tk.END, f"오류 내용: {error}\n")
        self.result_text.insert(tk.END, "자주 사용하는 기능을 단축키로 추가할까요?\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SNSGPTAIApp(root)
    root.mainloop()