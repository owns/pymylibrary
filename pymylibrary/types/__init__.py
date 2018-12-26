from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Boolean, SmallInteger, Integer, BigInteger, Numeric, CHAR, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

parse_utc = lambda s: datetime.strptime(s,'%Z %Y-%m-%d %H:%M:%S.%f') #"UTC 2017-02-26 17:06:05"    "UTC 2018-11-19 10:22:17.400"

Base = declarative_base()

__all__ = ['Track', 'File', 'Movie']

Base = declarative_base()

class Track(Base):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'))

    track_type = Column(String(30), nullable=False)
    default = Column(Boolean, nullable=False)
    track_id = Column(Integer, nullable=True)

    lang = Column(CHAR(2), nullable=True)
    format = Column(String(62), nullable=True)

    frame_rate = Column(Numeric(9,3), nullable=True)
    duration = Column(Integer, nullable=True)

    # video specific
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    # audio specific
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    channel_positions = Column(String(126), nullable=True)

    # video: width, height
    # audio: sample_rate, channel_s, channel_positions
    # both: frame_rate, duration,

    # track_type
    #           bit_rate,bit_rate_mode,
    #           internet_media_type,default
    # General   duration,frame_rate,file_size,codecs_video,audio_language_list,audio_codecs
    # Video     width,height,frame_rate,encoded_library_name
    #           color_space,chroma_subsampling

    @classmethod
    def from_mediainfo_track(cls, t):
        return Track(**cls.dict_from_mediainfo_track(t))
    
    @classmethod
    def dict_from_mediainfo_track(cls, t):
        return dict(
            track_type=t.track_type,
            default=t.default == 'Yes',
            track_id=t.track_id,
            lang=t.language,
            format=t.format,
            frame_rate=t.frame_rate,
            duration=t.duration,
            # video
            width=t.width,
            height=t.height,
            # Audio
            sample_rate=t.sample_rate,
            channels=t.channel_s,
            channel_positions=t.channel_positions)
    
    def __str__(self):
        return f"id={self.id} type={self.track_type} fmt={self.format}"

    def __repr__(self):
        return "<{0}({1!r})>".format(self.__class__.__name__, str(self))


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)

    # type: General

    # tracks
    tracks = relationship(Track, backref='file')

    # file info
    original_complete_name = Column(String, nullable=False)  #complete_name
    complete_name = Column(String, nullable=False) #complete_name
    file_extension = Column(String(260), nullable=False)

    file_size = Column(BigInteger, nullable=False)
    created = Column(DateTime(timezone=True), nullable=False) #file_creation_date
    last_mod = Column(DateTime(timezone=True), nullable=False) #file_last_modification_date
    
    # video info
    duration = Column(Integer, nullable=True) # milliseconds
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    # counts of streams
    count = Column(Integer, nullable=False)
    count_of_menu_streams = Column(SmallInteger, nullable=False)
    count_of_audio_streams = Column(SmallInteger, nullable=False)
    # audio_language_list
    count_of_text_streams = Column(SmallInteger, nullable=False)
    # text_format_list, text_language_list
    count_of_video_streams = Column(SmallInteger, nullable=False)
    # video_format_list, video_language_list

    @classmethod
    def from_mediainfo(cls, m):
        # create parent
        f = File(**cls.dict_from_mediainfo(m))
        # create all tracks
        f.tracks.extend(Track(**Track.dict_from_mediainfo_track(t)) for t in m.tracks if t.track_type != 'General')
        # return parent
        return f
    
    @classmethod
    def dict_from_mediainfo(cls, m):
        # get general track
        t = [t for t in m.tracks if t.track_type == 'General'][0]
        return dict(
            original_complete_name=t.complete_name,
            complete_name=t.complete_name,
            file_extension=t.file_extension,
            file_size=t.file_size,
            created= parse_utc(t.file_creation_date),
            last_mod=parse_utc(t.file_last_modification_date),
            duration=t.duration,
            title=t.title,
            description=t.description,
            count=t.count or 0,
            count_of_menu_streams=t.count_of_menu_streams or 0,
            count_of_audio_streams=t.count_of_audio_streams or 0,
            count_of_text_streams=t.count_of_text_streams or 0,
            count_of_video_streams=t.count_of_video_streams or 0)
    
    def __str__(self):
        return f"id={self.id} file={self.complete_name}"

    def __repr__(self):
        return "<{0}({1!r})>".format(self.__class__.__name__, str(self))


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    # main movie file index
    # movie_name
    # files


    # def __str__(self):
    #     return f"id={self.track_id} type={self.track_type} fmt={self.format}"

    def __repr__(self):
        return "<{0}({1!r})>".format(self.__class__.__name__, str(self))