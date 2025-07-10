FROM ubuntu:22.04
WORKDIR /app
COPY . /app
#COPY /usr/share/fonts /usr/share/fonts
# COPY ./sources.list /etc/apt/
#RUN apt update && apt-get -y install ca-certificates && sed -i "s@http://.*archive.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && sed -i "s@http://.*security.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && apt update
RUN  dpkg -i perl-base_5.34.0-3ubuntu1.4_amd64.deb libc6_2.35-0ubuntu3_amd64.deb debconf_1.5.79ubuntu1_all.deb libssl3_3.0.2-0ubuntu1_amd64.deb openssl_3.0.2-0ubuntu1_amd64.deb 'ca-certificates_20240203~22.04.1_all.deb'  && sed -i "s@http://.*archive.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && sed -i "s@http://.*security.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && apt update
RUN RUN rm -f perl-base_5.34.0-3ubuntu1.4_amd64.deb libc6_2.35-0ubuntu3_amd64.deb debconf_1.5.79ubuntu1_all.deb libssl3_3.0.2-0ubuntu1_amd64.deb openssl_3.0.2-0ubuntu1_amd64.deb 'ca-certificates_20240203~22.04.1_all.deb'
# 安装 locales 和中文语言包，生成 zh_CN.UTF-8 环境
RUN apt install python3 python3-pip  libreoffice ffmpeg lame nginx memcached locales language-pack-zh-hans  net-tools vim iputils-ping samba samba-common-bin python3-dev default-libmysqlclient-dev build-essential pkg-config -y && locale-gen zh_CN.UTF-8 
#RUN rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
COPY ./lib/ /usr/local/lib/python3.10/dist-packages/extractous/
RUN chmod +x /app/start.sh
# RUN python3 manage.py makemigrations app_knowledge_base


COPY ./smb.conf /etc/samba/
# RUN useradd --system --no-create-home --shell /usr/sbin/nologin baba && groupadd smbsharedgroup && usermod -aG smbsharedgroup baba && usermod -aG smbsharedgroup root

# RUN echo -e "baba@baba666\nbaba@baba666" | smbpasswd -s -a baba
RUN mkdir /app/knowledge_base/smb > /dev/null 2>&1 || true
#; chown -R root:smbsharedgroup /app/knowledge_base/smb 
#chmod 775 -R /app/knowledge_base/smb && chmod g+s -R /app/knowledge_base/smb && 
RUN chmod 775 -R /app/knowledge_base && service smbd reload
RUN chmod 755 -R convert_html ; chmod 755 -R convert_pdf ; chmod 755 -R convert_to_mp3 ; chmod 755 -R convert_video_voice ; chmod 755 -R craw_url_to_html ; chmod 755 -R app_knowledge_base/static ; chmod 755 -R github_repos ; chmod +x /app/cron/cron.sh


CMD ["/app/start.sh"]
