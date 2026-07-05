import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import User from '@/pages/User.vue'
import UserList from '@/pages/UserList.vue'
import ResumeSettings from '@/pages/ResumeSettings.vue'
import ResumePdf from '@/pages/ResumePdf.vue'
import ResumeView from '@/pages/ResumeView.vue'
import News from '@/pages/News.vue'
import NewsDetail from '@/pages/NewsDetail.vue'
import PreviewNews from '@/pages/preview_news.vue'
import DeleteNews from '@/pages/delete_news.vue'
import About from '@/pages/About.vue'
import Team from '@/pages/Team.vue'
import Career from '@/pages/Career.vue'
import InternApply from '@/pages/InternApply.vue'
import InternManage from '@/pages/InternManage.vue'
import BroadcastMessage from '@/pages/BroadcastMessage.vue'
import TaskPublish from '@/pages/TaskPublish.vue'
import TaskList from '@/pages/TaskList.vue'
import MyTasks from '@/pages/MyTasks.vue'
import TaskDetail from '@/pages/TaskDetail.vue'
import TaskSubmissions from '@/pages/TaskSubmissions.vue'
import ComingSoon from '@/pages/ComingSoon.vue'
import JoinUs from '@/pages/JoinUs.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/about', name: 'about', component: About },
  { path: '/team', name: 'team', component: Team },
  { path: '/career', name: 'career', component: Career },
  { path: '/career/intern-apply', name: 'intern-apply', component: InternApply },
  { path: '/career/join', name: 'join-us', component: JoinUs },
  { path: '/news', name: 'news', component: News },
  { path: '/news/preview', name: 'news-preview', component: PreviewNews },
  { path: '/news/delete', name: 'news-delete', component: DeleteNews },
  { path: '/news/:slug', name: 'news-detail', component: NewsDetail },
  { path: '/login', name: 'login', component: Login },
  { path: '/register', name: 'register', component: Register },
  { path: '/user', name: 'user', component: User },
  { path: '/user/resume', name: 'resume-settings', component: ResumeSettings },
  { path: '/user/resume-pdf', name: 'resume-pdf', component: ResumePdf },
  { path: '/user/resume/:userId', name: 'resume-view', component: ResumeView },
  { path: '/user/list', name: 'user-list', component: UserList },
  { path: '/user/interns', name: 'intern-manage', component: InternManage },
  { path: '/user/broadcast', name: 'broadcast-message', component: BroadcastMessage },
  { path: '/user/task-publish', name: 'task-publish', component: TaskPublish },
  { path: '/user/tasks', name: 'task-list', component: TaskList },
  { path: '/user/my-tasks', name: 'my-tasks', component: MyTasks },
  { path: '/user/task/:taskId', name: 'task-detail', component: TaskDetail },
  { path: '/user/tasks/:taskId/submissions', name: 'task-submissions', component: TaskSubmissions },
  { path: '/coming-soon', name: 'coming-soon', component: ComingSoon },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router

