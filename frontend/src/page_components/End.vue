<template>
    <section class="end-page">
      <!-- 顶部订阅 -->
      <div class="subscribe-row">
        <h2 class="subscribe-title">{{ $t('footer.subscribeTitle') }}</h2>
  
        <div class="subscribe-input">
          <input type="email" :placeholder="$t('footer.emailPlaceholder')" />
          <button class="subscribe-btn">➜</button>
        </div>
      </div>
  
      <hr />
  
      <!-- 主体五列信息 -->
      <div class="footer-grid">
        <!-- 左侧：动态 Social 卡片 -->
        <div class="col logo-col">
          <div class="social-card-wrapper">
            <div class="card">
              <div class="background"></div>
  
              <div class="logo">
                <img :src="dailLogo" :alt="$t('footer.dailLogoAlt')" class="logo-img" />
              </div>
  
              <a href="#">
                <div class="box box1">
                  <span class="icon">
                    <svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg" class="svg">
                      <path
                        d="M 9.9980469 3 C 6.1390469 3 3 6.1419531 3 10.001953 L 3 20.001953 C 3 23.860953 6.1419531 27 10.001953 27 L 20.001953 27 C 23.860953 27 27 23.858047 27 19.998047 L 27 9.9980469 C 27 6.1390469 23.858047 3 19.998047 3 L 9.9980469 3 z M 22 7 C 22.552 7 23 7.448 23 8 C 23 8.552 22.552 9 22 9 C 21.448 9 21 8.552 21 8 C 21 7.448 21.448 7 22 7 z M 15 9 C 18.309 9 21 11.691 21 15 C 21 18.309 18.309 21 15 21 C 11.691 21 9 18.309 9 15 C 9 11.691 11.691 9 15 9 z M 15 11 A 4 4 0 0 0 11 15 A 4 4 0 0 0 15 19 A 4 4 0 0 0 19 15 A 4 4 0 0 0 15 11 z">
                      </path>
                    </svg>
                  </span>
                </div>
              </a>
  
              <a href="##">
                <div class="box box2">
                  <span class="icon">
                    <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" class="svg">
                      <path
                        d="M459.37 151.716c.325 4.548.325 9.097.325 13.645 0 138.72-105.583 298.558-298.558 298.558-59.452 0-114.68-17.219-161.137-47.106 8.447.974 16.568 1.299 25.34 1.299 49.055 0 94.213-16.568 130.274-44.832-46.132-.975-84.792-31.188-98.112-72.772 6.498.974 12.995 1.624 19.818 1.624 9.421 0 18.843-1.3 27.614-3.573-48.081-9.747-84.143-51.98-84.143-102.985v-1.299c13.969 7.797 30.214 12.67 47.431 13.319-28.264-18.843-46.781-51.005-46.781-87.391 0-19.492 5.197-37.36 14.294-52.954 51.655 63.675 129.3 105.258 216.365 109.807-1.624-7.797-2.599-15.918-2.599-24.04 0-57.828 46.782-104.934 104.934-104.934 30.213 0 57.502 12.67 76.67 33.137 23.715-4.548 46.456-13.32 66.599-25.34-7.798 24.366-24.366 44.833-46.132 57.827 21.117-2.273 41.584-8.122 60.426-16.243-14.292 20.791-32.161 39.308-52.628 54.253z">
                      </path>
                    </svg>
                  </span>
                </div>
              </a>
  
              <a href="###">
                <div class="box box3">
                  <span class="icon">
                    <svg viewBox="0 0 640 512" xmlns="http://www.w3.org/2000/svg" class="svg">
                      <path
                        d="M524.531,69.836a1.5,1.5,0,0,0-.764-.7A485.065,485.065,0,0,0,404.081,32.03a1.816,1.816,0,0,0-1.923.91,337.461,337.461,0,0,0-14.9,30.6,447.848,447.848,0,0,0-134.426,0,309.541,309.541,0,0,0-15.135-30.6,1.89,1.89,0,0,0-1.924-.91A483.689,483.689,0,0,0,116.085,69.137a1.712,1.712,0,0,0-.788.676C39.068,183.651,18.186,294.69,28.43,404.354a2.016,2.016,0,0,0,.765,1.375A487.666,487.666,0,0,0,176.02,479.918a1.9,1.9,0,0,0,2.063-.676A348.2,348.2,0,0,0,208.12,430.4a1.86,1.86,0,0,0-1.019-2.588,321.173,321.173,0,0,1-45.868-21.853,1.885,1.885,0,0,1-.185-3.126c3.082-2.309,6.166-4.711,9.109-7.137a1.819,1.819,0,0,1,1.9-.256c96.229,43.917,200.41,43.917,295.5,0a1.812,1.812,0,0,1,1.924.233c2.944,2.426,6.027,4.851,9.132,7.16a1.884,1.884,0,0,1-.162,3.126,301.407,301.407,0,0,1-45.89,21.83,1.875,1.875,0,0,0-1,2.611,391.055,391.055,0,0,0,30.014,48.815,1.864,1.864,0,0,0,2.063.7A486.048,486.048,0,0,0,610.7,405.729a1.882,1.882,0,0,0,.765-1.352C623.729,277.594,590.933,167.465,524.531,69.836ZM222.491,337.58c-28.972,0-52.844-26.587-52.844-59.239S193.056,219.1,222.491,219.1c29.665,0,53.306,26.82,52.843,59.239C275.334,310.993,251.924,337.58,222.491,337.58Zm195.38,0c-28.971,0-52.843-26.587-52.843-59.239S388.437,219.1,417.871,219.1c29.667,0,53.307,26.82,52.844,59.239C470.715,310.993,447.538,337.58,417.871,337.58Z">
                      </path>
                    </svg>
                  </span>
                </div>
              </a>
  
              <div class="box box4"></div>
            </div>
          </div>
        </div>
  
        <!-- Solutions -->
        <div class="col">
          <p class="col-title">{{ $t('footer.solutionsTitle') }}</p>
          <ul>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.solutions1') }}</li>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.solutions2') }}</li>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.solutions3') }}</li>
          </ul>
        </div>
  
        <!-- Technology -->
        <div class="col">
          <p class="col-title">{{ $t('footer.technologyTitle') }}</p>
          <ul>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.technology1') }}</li>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.technology2') }}</li>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.technology3') }}</li>
          </ul>
        </div>
  
        <!-- Company -->
        <div class="col">
          <p class="col-title">{{ $t('footer.companyTitle') }}</p>
          <ul>
            <li @click="$router.push('/about')">{{ $t('footer.company1') }}</li>
            <li @click="$router.push('/team')">{{ $t('footer.company2') }}</li>
            <li @click="$router.push('/career')">{{ $t('footer.company3') }}</li>
            <li @click="$router.push('/news')">{{ $t('footer.company4') }}</li>
          </ul>
        </div>
  
        <!-- Docs -->
        <div class="col">
          <p class="col-title">{{ $t('footer.docsTitle') }}</p>
          <ul>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.docs1') }}</li>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.docs2') }}</li>
            <li @click="$router.push('/coming-soon')">{{ $t('footer.docs3') }}</li>
          </ul>
        </div>
      </div>
  
      <hr />
  
      <!-- 社交媒体 -->
      <div class="social-row">
        <div class="social-icons">
          <div class="icon-round">
            <img src="@/assets/images/end-1.png" :alt="$t('footer.socialAlt', { n: 1 })" />
          </div>
          <div class="icon-round">
            <img src="@/assets/images/end-2.png" :alt="$t('footer.socialAlt', { n: 2 })" />
          </div>
          <div class="icon-round">
            <img src="@/assets/images/end-3.png" :alt="$t('footer.socialAlt', { n: 3 })" />
          </div>
          <div class="icon-round">
            <img src="@/assets/images/end-4.png" :alt="$t('footer.socialAlt', { n: 4 })" />
          </div>
          <div class="icon-round">
            <img src="@/assets/images/end-5.png" :alt="$t('footer.socialAlt', { n: 5 })" />
          </div>
        </div>
  
        <p class="copyright">{{ $t('footer.rights') }}</p>
  
        <p class="address">{{ $t('footer.address') }}</p>
      </div>
    </section>
  </template>
  
  <script setup>
  import dailLogo from '@/assets/images/DAIL.png'
  </script>
  
  <style scoped>
  .end-page {
    padding: 80px 8vw;
    width: 100%;
    min-width: 0;
    background: #ffffff;
    color: #000;
    font-family: "Inter", system-ui, sans-serif;
  }
  
  /* 顶部区域 */
  .subscribe-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 90px;
    transform: translateY(-30px);
  }
  
  .subscribe-title {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.02em;
    transform: scaleY(1.10);        /* 轻微拉长纵向笔画 */
    transform-origin: left center;
  }
  
  .subscribe-input {
    display: flex;
    border: 1px solid #ddd;
    border-radius: 30px;
    overflow: hidden;
    width: 320px;
  }
  
  .subscribe-input input {
    flex: 1;
    padding: 12px 16px;
    border: none;
    outline: none;
  }
  
  .subscribe-btn {
    background: #000;
    color: #fff;
    padding: 0 20px;
    cursor: pointer;
    border: none;
  }
  
  hr {
    border: 0;
    border-top: 1px solid #eee;
    margin: 40px 0;
  }

  hr:first-of-type {
    margin-top: -60px;
  }
  
  /* 主体内容五列 */
  .footer-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr;
    gap: 40px;
    margin-bottom: 40px;
  }
  
  .logo-col {
    display: flex;
    align-items: flex-start;
  }
  
  /* 栏目 */
  .col-title {
    font-size: 16px;
    color: #666;
    letter-spacing: 0.05em;
    margin-bottom: 20px;
    font-weight: 500;
  }
  
  .col ul {
    list-style: none;
    padding: 0;
  }
  
  .col li {
    margin-bottom: 18px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
  }
  
  .col li:hover {
    text-decoration: underline;
  }
  
  /* 底部社交圆形按钮 */
  .social-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    margin-left: -30px;
  }
  
  .social-icons {
    display: flex;
    gap: 14px;
  }
  
  .icon-round {
    width: 44px;
    height: 44px;
    border: 1px solid #ddd;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    overflow: hidden;
  }

  .icon-round img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 8px;
    transition: all 0.3s ease;
  }
  
  .icon-round:hover {
    background: #000;
  }

  .icon-round:hover img {
    filter: brightness(0) invert(1);
  }
  
  .address {
    color: #666;
    font-size: 14px;
  }
  
  /* ========= 动态 Social 卡片样式 ========= */
  
  .card {
    position: relative;
    width: 200px;
    height: 200px;
    background: #f0f0f0;
    border-radius: 30px;
    overflow: hidden;
    box-shadow: rgba(0, 0, 0, 0.2) 0px 7px 29px 0px;
    transition: all 0.8s ease-in-out;
    border: 2px solid #fff;
  }
  
  .background {
    position: absolute;
    inset: 0;
    background-color: #000;
    background-image: linear-gradient(
      43deg,
      #000 0%,
      #333 46%,
      #ccc 100%
    );
  }
  
  .card .logo {
    position: absolute;
    right: 50%;
    bottom: 50%;
    transform: translate(50%, 50%);
    transition: all 0.6s ease-in-out;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .card .logo-img {
    width: 96px;
    height: auto;
    display: block;
    transition: transform 0.6s ease-in-out, filter 0.6s ease-in-out;
  }
  
  .icon {
    display: inline-block;
    width: 20px;
    height: 20px;
  }
  
  .icon .svg {
    fill: rgba(255, 255, 255, 0.797);
    width: 100%;
    transition: all 0.5s ease-in-out;
  }

  .copyright {
    font-size: 14px;
    color:#666;
    font-weight: 500;

  }
  
  .box {
    position: absolute;
    padding: 10px;
    text-align: right;
    background: rgba(255, 255, 255, 0.3);
    border-top: 2px solid rgb(255, 255, 255);
    border-right: 1px solid white;
    border-radius: 10% 13% 42% 0%/10% 12% 75% 0%;
    box-shadow: rgba(100, 100, 111, 0.5) -7px 7px 29px 0px;
    transform-origin: bottom left;
    transition: all 1s ease-in-out;
  }
  
  .box::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    opacity: 0;
    transition: all 0.5s ease-in-out;
  }
  
  .box:hover .svg {
    fill: white;
  }
  
  .box1 {
    width: 70%;
    height: 70%;
    bottom: -70%;
    left: -70%;
  }
  
  .box1::before {
    background: radial-gradient(
      circle at 30% 107%,
      #bcbcbc 0%,
      #666666 90%
    );
  }
  
  .box1:hover::before {
    opacity: 1;
  }
  
  .box1:hover .icon .svg {
    filter: drop-shadow(0 0 5px white);
  }
  
  .box2 {
    width: 50%;
    height: 50%;
    bottom: -50%;
    left: -50%;
    transition-delay: 0.2s;
  }
  
  .box2::before {
    background: radial-gradient(
      circle at 30% 107%,
      #333333 0%,
      #1c1c1c 90%
    );
  }
  
  .box2:hover::before {
    opacity: 1;
  }
  
  .box2:hover .icon .svg {
    filter: drop-shadow(0 0 5px white);
  }
  
  .box3 {
    width: 30%;
    height: 30%;
    bottom: -30%;
    left: -30%;
    transition-delay: 0.4s;
  }
  
  .box3::before {
    background: radial-gradient(
      circle at 30% 107%,
      #666666 0%,
      #333333 90%
    );
  }
  
  .box3:hover::before {
    opacity: 1;
  }
  
  .box3:hover .icon .svg {
    filter: drop-shadow(0 0 5px white);
  }
  
  .box4 {
    width: 10%;
    height: 10%;
    bottom: -10%;
    left: -10%;
    transition-delay: 0.6s;
  }
  
  .card:hover {
    transform: scale(1.06);
  }
  
  .card:hover .box {
    bottom: -1px;
    left: -1px;
  }
  
  .card:hover .logo {
    transform: translate(86px, -50px);
    letter-spacing: 0px;
  }

  .card:hover .logo-img {
    filter: invert(1);
    transform: translate(10px, -6px);
  }

  @media (max-width: 900px) {
    .end-page {
      width: 100%;
      min-width: 0;
      padding: 64px 20px 32px;
    }

    .subscribe-row {
      margin-bottom: 32px;
      transform: none;
      flex-direction: column;
      align-items: stretch;
      gap: 20px;
    }

    .subscribe-title {
      font-size: 24px;
      line-height: 1.3;
      transform: none;
    }

    .subscribe-input {
      width: 100%;
      min-height: 50px;
    }

    .subscribe-input input {
      min-width: 0;
    }

    .subscribe-btn {
      min-width: 58px;
    }

    hr,
    hr:first-of-type {
      margin: 32px 0;
    }

    .footer-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 32px 20px;
      margin-bottom: 32px;
    }

    .logo-col {
      grid-column: 1 / -1;
    }

    .card {
      width: 160px;
      height: 160px;
      border-radius: 24px;
    }

    .card .logo-img {
      width: 80px;
    }

    .col-title {
      margin-bottom: 14px;
      font-size: 14px;
    }

    .col li {
      min-height: 36px;
      margin-bottom: 8px;
      font-size: 15px;
      line-height: 1.45;
    }

    .social-row {
      margin-left: 0;
      flex-direction: column;
      align-items: flex-start;
      gap: 18px;
    }

    .social-icons {
      width: 100%;
      flex-wrap: wrap;
      gap: 10px;
    }

    .icon-round {
      width: 42px;
      height: 42px;
    }
  }
  </style>
