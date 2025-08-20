"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  FileText,
  MapPin,
  Briefcase,
  Download,
  Heart,
  ThumbsDown,
  Send,
  Paperclip,
  Filter,
  Undo2,
  CheckCircle,
  XCircle,
  Menu,
  Plus,
  MessageSquare,
  Clock,
} from "lucide-react"

interface Candidate {
  id: string
  name: string
  role: string
  avatar: string
  skills: string[]
  location: string
  experience: string
  cvUrl: string
  initials: string
  gradientFrom: string
  gradientTo: string
}

interface Message {
  id: string
  type: "bot" | "user"
  content: string
  candidates?: Candidate[]
  timestamp: Date
}

interface ChatHistory {
  id: string
  title: string
  lastMessage: string
  timestamp: Date
  messageCount: number
}

const mockCandidates: Candidate[] = [
  {
    id: "1",
    name: "Sarah Chen",
    role: "Senior Software Engineer",
    avatar: "/professional-woman-developer.png",
    skills: ["React", "TypeScript", "Node.js", "AWS"],
    location: "San Francisco, CA",
    experience: "5+ years",
    cvUrl: "/mock-cv.pdf",
    initials: "SC",
    gradientFrom: "#667eea",
    gradientTo: "#764ba2",
  },
  {
    id: "2",
    name: "Marcus Johnson",
    role: "Full Stack Developer",
    avatar: "/professional-man-developer.png",
    skills: ["Python", "Django", "PostgreSQL", "Docker"],
    location: "New York, NY",
    experience: "4+ years",
    cvUrl: "/mock-cv.pdf",
    initials: "MJ",
    gradientFrom: "#f093fb",
    gradientTo: "#f5576c",
  },
  {
    id: "3",
    name: "Elena Rodriguez",
    role: "Frontend Developer",
    avatar: "/professional-woman-frontend-developer.png",
    skills: ["Vue.js", "JavaScript", "CSS", "Figma"],
    location: "Austin, TX",
    experience: "3+ years",
    cvUrl: "/mock-cv.pdf",
    initials: "ER",
    gradientFrom: "#4facfe",
    gradientTo: "#00f2fe",
  },
]

const mockChatHistory: ChatHistory[] = [
  {
    id: "1",
    title: "Senior Software Engineer Search",
    lastMessage: "Found 3 excellent candidates for this role",
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    messageCount: 12,
  },
  {
    id: "2",
    title: "Frontend Developer Hiring",
    lastMessage: "Shortlisted 2 candidates for interview",
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
    messageCount: 8,
  },
  {
    id: "3",
    title: "Product Manager Role",
    lastMessage: "Reviewing candidate portfolios",
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
    messageCount: 15,
  },
]

export default function HirePalChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "bot",
      content: "Hello 👋 this is HirePal. I'm your Deloitte recruiting assistant. What role are you hiring for today?",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [selectedCv, setSelectedCv] = useState<string | null>(null)
  const [currentCandidateIndex, setCurrentCandidateIndex] = useState<{ [messageId: string]: number }>({})
  const [swipeDirection, setSwipeDirection] = useState<{ [candidateId: string]: "left" | "right" | null }>({})
  const [recentlyRejected, setRecentlyRejected] = useState<{
    candidateId: string
    messageId: string
    timestamp: number
  } | null>(null)
  const [candidateActions, setCandidateActions] = useState<{
    [candidateId: string]: "shortlisted" | "rejected" | null
  }>({})
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>(mockChatHistory)
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")

    // Simulate bot response with candidates
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: "Great! I found some excellent candidates for this role. Here are the top matches:",
        candidates: mockCandidates,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
      setCurrentCandidateIndex((prev) => ({ ...prev, [botMessage.id]: 0 }))
    }, 1000)
  }

  const handleSwipe = (candidateId: string, direction: "left" | "right", messageId: string) => {
    setSwipeDirection((prev) => ({ ...prev, [candidateId]: direction }))

    const action = direction === "right" ? "shortlisted" : "rejected"
    setCandidateActions((prev) => ({ ...prev, [candidateId]: action }))

    if (direction === "left") {
      setRecentlyRejected({ candidateId, messageId, timestamp: Date.now() })
      setTimeout(() => {
        setRecentlyRejected((prev) => (prev?.candidateId === candidateId ? null : prev))
      }, 5000)
    }

    const candidate = mockCandidates.find((c) => c.id === candidateId)

    setTimeout(() => {
      const currentIndex = currentCandidateIndex[messageId] || 0
      const candidates = messages.find((m) => m.id === messageId)?.candidates || []

      if (currentIndex < candidates.length - 1) {
        setCurrentCandidateIndex((prev) => ({ ...prev, [messageId]: currentIndex + 1 }))
      } else {
        const completionMessage: Message = {
          id: (Date.now() + Math.random()).toString(),
          type: "bot",
          content:
            "Great! You've reviewed all candidates. Would you like me to find more matches or help with the next steps?",
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, completionMessage])
      }

      setSwipeDirection((prev) => ({ ...prev, [candidateId]: null }))
    }, 400)
  }

  const handleUndo = () => {
    if (!recentlyRejected) return

    const { candidateId, messageId } = recentlyRejected

    setCandidateActions((prev) => ({ ...prev, [candidateId]: null }))

    const currentIndex = currentCandidateIndex[messageId] || 0
    setCurrentCandidateIndex((prev) => ({ ...prev, [messageId]: Math.max(0, currentIndex - 1) }))

    setRecentlyRejected(null)
  }

  const handleDownloadCV = (candidate: Candidate) => {
    const link = document.createElement("a")
    link.href = candidate.cvUrl
    link.download = `${candidate.name.replace(" ", "_")}_CV.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleNewChat = () => {
    // Save current chat to history if it has messages
    if (messages.length > 1) {
      const newHistoryItem: ChatHistory = {
        id: Date.now().toString(),
        title: messages[1]?.content.slice(0, 30) + "..." || "New Chat",
        lastMessage: messages[messages.length - 1]?.content || "",
        timestamp: new Date(),
        messageCount: messages.length,
      }
      setChatHistory((prev) => [newHistoryItem, ...prev])
    }

    // Reset to initial state
    setMessages([
      {
        id: "1",
        type: "bot",
        content:
          "Hello 👋 this is HirePal. I'm your Deloitte recruiting assistant. What role are you hiring for today?",
        timestamp: new Date(),
      },
    ])
    setCurrentChatId(null)
    setCandidateActions({})
    setCurrentCandidateIndex({})
    setSidebarOpen(false)
  }

  const handleLoadChat = (chatId: string) => {
    setCurrentChatId(chatId)
    // In a real app, you would load the actual chat messages here
    setSidebarOpen(false)
  }

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))

    if (diffInHours < 1) return "Just now"
    if (diffInHours < 24) return `${diffInHours}h ago`
    const diffInDays = Math.floor(diffInHours / 24)
    if (diffInDays < 7) return `${diffInDays}d ago`
    return date.toLocaleDateString()
  }

  const CandidateCard = ({ candidate, messageId }: { candidate: Candidate; messageId: string }) => {
    const swipeClass =
      swipeDirection[candidate.id] === "left"
        ? "swipe-left"
        : swipeDirection[candidate.id] === "right"
          ? "swipe-right"
          : ""

    const candidateAction = candidateActions[candidate.id]

    return (
      <Card
        className={`w-full max-w-sm mx-auto bg-white/95 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-gray-100/50 ${swipeClass} hover:scale-[1.02] transform relative overflow-hidden`}
      >
        <div className="absolute -top-8 -right-8 w-24 h-24 bg-gradient-to-br from-[#86BC25]/10 to-[#7AA622]/5 rounded-full" />
        <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-gradient-to-tr from-[#0F0B0B]/5 to-transparent rounded-full" />
        <div className="absolute inset-0 bg-gradient-to-br from-white/50 to-transparent pointer-events-none" />

        {candidateAction && (
          <div className="absolute top-4 right-4 z-10">
            {candidateAction === "shortlisted" ? (
              <div className="flex items-center space-x-1 bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-semibold">
                <CheckCircle className="w-3 h-3" />
                <span>Shortlisted</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1 bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-semibold">
                <XCircle className="w-3 h-3" />
                <span>Passed</span>
              </div>
            )}
          </div>
        )}

        <CardContent className="p-8 relative">
          <div className="flex flex-col items-center space-y-6">
            <div
              className="w-24 h-24 rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-xl ring-4 ring-white/30 hover:ring-white/50 transition-all duration-300"
              style={{
                background: `linear-gradient(135deg, ${candidate.gradientFrom} 0%, ${candidate.gradientTo} 100%)`,
              }}
            >
              {candidate.initials}
            </div>

            <div className="text-center space-y-3">
              <h3 className="font-bold text-xl text-[#0F0B0B] tracking-tight">{candidate.name}</h3>
              <p className="text-gray-600 font-semibold text-base">{candidate.role}</p>
              <div className="flex flex-col space-y-2 text-sm">
                <div className="flex items-center justify-center text-gray-500 space-x-2">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <span className="font-medium">{candidate.location}</span>
                </div>
                <div className="flex items-center justify-center text-gray-500 space-x-2">
                  <Briefcase className="w-4 h-4 text-gray-400" />
                  <span className="font-medium">{candidate.experience}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 justify-center max-w-full">
              {candidate.skills.map((skill, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="text-xs px-3 py-1.5 bg-gradient-to-r from-gray-100 to-gray-50 text-gray-700 border border-gray-200/50 font-semibold hover:from-gray-200 hover:to-gray-100 transition-all duration-200 shadow-sm"
                >
                  {skill}
                </Badge>
              ))}
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedCv(candidate.cvUrl)}
              className="w-full flex items-center justify-center space-x-2 border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 py-3 font-semibold shadow-sm hover:shadow-md"
            >
              <FileText className="w-4 h-4" />
              <span>View CV</span>
            </Button>

            <div className="flex space-x-3 w-full">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSwipe(candidate.id, "left", messageId)}
                className="flex-1 border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 transition-all duration-200 py-3 font-semibold shadow-sm hover:shadow-md bg-transparent group"
                disabled={!!candidateAction}
              >
                <ThumbsDown className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                Pass
              </Button>
              <Button
                size="sm"
                onClick={() => handleSwipe(candidate.id, "right", messageId)}
                className="flex-1 bg-gradient-to-r from-[#86BC25] to-[#7AA622] hover:from-[#7AA622] hover:to-[#6B9419] text-white shadow-lg hover:shadow-xl transition-all duration-200 py-3 font-semibold border-0 group"
                disabled={!!candidateAction}
              >
                <Heart className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                Shortlist
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 relative overflow-hidden">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-80 bg-white/95 backdrop-blur-xl border-r border-gray-200/30 shadow-xl transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Sidebar Header */}
          <div className="p-6 border-b border-gray-200/30">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-lg text-[#0F0B0B]">Chat History</h2>
              <Button onClick={() => setSidebarOpen(false)} variant="ghost" size="sm">
                ✕
              </Button>
            </div>
            <Button
              onClick={handleNewChat}
              className="w-full bg-gradient-to-r from-[#86BC25] to-[#7AA622] hover:from-[#7AA622] hover:to-[#6B9419] text-white shadow-lg hover:shadow-xl transition-all duration-200 font-semibold"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>
          </div>

          {/* Chat History List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatHistory.map((chat) => (
              <Card
                key={chat.id}
                className={`cursor-pointer transition-all duration-200 hover:shadow-md border border-gray-200/50 ${
                  currentChatId === chat.id ? "bg-[#86BC25]/5 border-[#86BC25]/30" : "bg-white/80 hover:bg-gray-50/80"
                }`}
                onClick={() => handleLoadChat(chat.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-[#86BC25]/20 to-[#7AA622]/10 rounded-xl flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-5 h-5 text-[#86BC25]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm text-[#0F0B0B] truncate mb-1">{chat.title}</h3>
                      <p className="text-xs text-gray-600 line-clamp-2 mb-2">{chat.lastMessage}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatTimeAgo(chat.timestamp)}</span>
                        </div>
                        <span className="bg-gray-100 px-2 py-0.5 rounded-full font-medium">{chat.messageCount}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 relative overflow-hidden">
        {/* Deloitte signature circular background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {/* Large primary circle - top right */}
          <div className="absolute -top-32 -right-32 w-96 h-96 bg-gradient-to-br from-[#86BC25]/8 to-[#86BC25]/3 rounded-full blur-3xl" />

          {/* Medium circle - bottom left */}
          <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-gradient-to-tr from-[#0F0B0B]/5 to-[#0F0B0B]/2 rounded-full blur-2xl" />

          {/* Small accent circles */}
          <div className="absolute top-1/3 left-1/4 w-32 h-32 bg-gradient-to-br from-[#86BC25]/6 to-transparent rounded-full blur-xl" />
          <div className="absolute bottom-1/3 right-1/4 w-24 h-24 bg-gradient-to-tl from-[#0F0B0B]/4 to-transparent rounded-full blur-lg" />

          {/* Micro circles for texture */}
          <div className="absolute top-1/4 right-1/3 w-16 h-16 bg-[#86BC25]/4 rounded-full blur-md" />
          <div className="absolute bottom-1/4 left-1/3 w-12 h-12 bg-[#0F0B0B]/3 rounded-full blur-sm" />

          {/* Subtle grid pattern overlay */}
          <div
            className="absolute inset-0 opacity-[0.02]"
            style={{
              backgroundImage: `radial-gradient(circle at 1px 1px, #0F0B0B 1px, transparent 0)`,
              backgroundSize: "40px 40px",
            }}
          />
        </div>

        <div className="bg-white/95 backdrop-blur-xl border-b border-gray-200/30 p-6 shadow-sm relative overflow-hidden z-10">
          <div className="absolute -top-4 -right-4 w-20 h-20 bg-gradient-to-br from-[#86BC25]/10 to-transparent rounded-full" />
          <div className="flex items-center justify-between relative">
            <div className="flex items-center space-x-4">
              {/* Menu button for sidebar toggle */}
              <Button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                variant="ghost"
                size="sm"
                className="p-2 hover:bg-gray-100"
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </Button>
              <div className="w-12 h-12 bg-gradient-to-br from-[#86BC25] to-[#7AA622] rounded-2xl flex items-center justify-center shadow-lg relative">
                <span className="text-white font-bold text-xl">H</span>
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-[#0F0B0B] rounded-full border-2 border-white" />
              </div>
              <div>
                <h1 className="font-bold text-[#0F0B0B] text-lg tracking-tight">HirePal</h1>
                <p className="text-sm text-gray-500 font-medium">Deloitte Recruiting Assistant</p>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-lg text-[#0F0B0B]">Deloitte</div>
              <div className="text-xs text-gray-500 font-medium tracking-wider">DIGITAL</div>
            </div>
          </div>
        </div>

        {recentlyRejected && (
          <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border-b border-orange-200/50 px-6 py-3 flex items-center justify-between animate-in slide-in-from-top duration-300 z-10">
            <div className="flex items-center space-x-3">
              <XCircle className="w-4 h-4 text-orange-600" />
              <span className="text-sm font-medium text-orange-800">Candidate rejected. Changed your mind?</span>
            </div>
            <Button
              onClick={handleUndo}
              size="sm"
              variant="outline"
              className="border-orange-300 text-orange-700 hover:bg-orange-100 hover:border-orange-400 transition-all duration-200 font-semibold bg-transparent"
            >
              <Undo2 className="w-4 h-4 mr-1" />
              Undo
            </Button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-6 space-y-6 relative z-10">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-xs lg:max-w-md px-5 py-3 rounded-3xl transition-all duration-200 ${
                  message.type === "user"
                    ? "bg-gradient-to-r from-[#86BC25] to-[#7AA622] text-white shadow-lg"
                    : "bg-white/90 backdrop-blur-xl text-gray-900 shadow-lg border border-gray-100/50"
                }`}
              >
                <p className="text-sm font-medium leading-relaxed">{message.content}</p>

                {message.candidates && message.candidates.length > 0 && (
                  <div className="mt-6">
                    {(() => {
                      const currentIndex = currentCandidateIndex[message.id] || 0
                      const candidate = message.candidates[currentIndex]
                      return candidate ? (
                        <div className="space-y-3">
                          <CandidateCard candidate={candidate} messageId={message.id} />
                          <div className="text-center text-xs text-gray-500 font-medium">
                            {currentIndex + 1} of {message.candidates.length} candidates
                          </div>
                        </div>
                      ) : null
                    })()}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <Dialog open={!!selectedCv} onOpenChange={() => setSelectedCv(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh] bg-white/98 backdrop-blur-xl border-0 shadow-2xl">
            <DialogHeader className="flex flex-row items-center justify-between">
              <DialogTitle className="text-xl font-bold text-gray-900">Candidate CV</DialogTitle>
              <Button
                onClick={() => {
                  const candidate = mockCandidates.find((c) => c.cvUrl === selectedCv)
                  if (candidate) handleDownloadCV(candidate)
                }}
                className="bg-gradient-to-r from-[#86BC25] to-[#7AA622] hover:from-[#7AA622] hover:to-[#6B9419] text-white shadow-lg hover:shadow-xl transition-all duration-200 font-semibold"
              >
                <Download className="w-4 h-4 mr-2" />
                Download CV
              </Button>
            </DialogHeader>
            <div className="flex-1 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-12 text-center border border-gray-200/50 max-w-md mx-auto">
              <FileText className="w-24 h-24 mx-auto text-gray-400 mb-6" />
              <p className="text-gray-700 text-xl font-semibold mb-2">CV Preview</p>
              <p className="text-sm text-gray-500 font-medium">PDF viewer would be integrated here in production</p>
              <div className="mt-8 p-6 bg-white/80 rounded-xl border border-gray-200/50 max-w-md mx-auto">
                <p className="text-xs text-gray-600 font-medium">Click "Download CV" above to save the full document</p>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        <div className="bg-white/95 backdrop-blur-xl border-t border-gray-200/30 p-6 shadow-lg relative overflow-hidden z-10">
          <div className="absolute -top-2 -left-2 w-12 h-12 bg-gradient-to-br from-[#86BC25]/5 to-transparent rounded-full" />
          <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-gradient-to-tl from-[#0F0B0B]/5 to-transparent rounded-full" />

          <div className="flex items-center space-x-4 max-w-4xl mx-auto relative">
            <Button
              variant="outline"
              size="sm"
              className="p-3 border-gray-200 hover:border-[#86BC25] hover:bg-[#86BC25]/5 transition-all duration-200 shadow-sm hover:shadow-md bg-transparent group"
            >
              <Paperclip className="w-4 h-4 text-gray-600 group-hover:text-[#86BC25]" />
            </Button>

            <Button
              variant="outline"
              size="sm"
              className="p-3 border-gray-200 hover:border-[#86BC25] hover:bg-[#86BC25]/5 transition-all duration-200 shadow-sm hover:shadow-md bg-transparent group"
            >
              <Filter className="w-4 h-4 text-gray-600 group-hover:text-[#86BC25]" />
            </Button>

            <div className="flex-1 relative">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                placeholder="Ask HirePal about candidates, roles, or hiring needs..."
                className="w-full px-4 py-3 rounded-2xl border-gray-200 focus:border-[#86BC25] focus:ring-[#86BC25] bg-white/90 backdrop-blur-sm shadow-sm hover:shadow-md transition-all duration-200 text-sm font-medium placeholder:text-gray-500"
              />
            </div>

            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim()}
              className="p-3 bg-gradient-to-r from-[#86BC25] to-[#7AA622] hover:from-[#7AA622] hover:to-[#6B9419] text-white shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-2xl"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
