<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { cpuModels } from './data/cpuModels'
import { motherboardChipsets } from './data/motherboardChipsets'
import { gpuModels } from './data/gpuModels'

const copy = {
  zh: {
    switchLanguage: 'EN', checkIngredients: '查查成分', clear: '清空配置', export: '导出配置', bilingualExport: '以中英文导出', selected: '已选', item: '项',
    heroTitle: '装机', heroSubtitle: '？！装装？！', heroCopy: '从处理器到机箱，循序完成属于你的硬件搭配。选择没有标准答案，只有更接近你工作方式的配置。', start: '开始配置',
    selectComponents: '选择组件', back: '返回全部组件', searchCpu: '在 {count} 个 CPU 型号中搜索', searchGpu: '在 {count} 个显卡型号中搜索', cpuPlaceholder: '例如：Ryzen 7 7800X3D 或 Core i5-14600K', gpuPlaceholder: '例如：RTX 5090 D V2、RX 9070 XT 或 Arc B580', boardSize: '主板规格',
    choose: '选择', chosen: '已选择', incompatible: '与已选 CPU、主板或内存不兼容', memoryIncompatible: '与已选 CPU 或主板的内存代际不兼容', memorySlots: '注意主板内存插槽', gpuSlots: '注意主板 PCIe 插槽', storagePorts: '注意主板存储接口',
    memoryChosen: '已选择 {count} / 4 条内存。{notice}', gpuChosen: '已选择 {count} / 4 张显卡。{notice}', storageChosen: 'PCIe {pcie} / 5，SATA + 机械硬盘 {other}。{notice}', clearMemory: '清空内存选择', clearGpu: '清空显卡选择', clearStorage: '清空存储选择', loadMore: '加载更多（已显示 {shown} / {total}）', noCpu: '没有匹配的 CPU 型号。', noGpu: '没有匹配的显卡型号。', selectedCount: '已选 {selected} / {total} 个组件', continue: '继续搭配', available: '可选', maxSupport: '最大支持', socket: '插槽',
    maxGpu: '最多可选择 4 张显卡。', maxMemory: '最多可选择 4 条内存。', memorySame: '已选择 {name}，内存条的代际和容量必须一致。', maxStorage: '{standard} 最多可选择 {count} 个。',
    exportTitle: '装机配置', exportTime: '导出时间', exportEmpty: '尚未选择任何组件。', bilingualTitle: 'PC Configuration / 装机配置', bilingualTime: 'Exported / 导出时间', bilingualEmpty: 'No components selected. / 尚未选择任何组件。',
  },
  en: {
    switchLanguage: '中文', checkIngredients: 'Ingredients', clear: 'Clear', export: 'Export', bilingualExport: 'Bilingual export', selected: 'Selected', item: 'items',
    heroTitle: 'BUILD', heroSubtitle: '?! BUILD ?!', heroCopy: 'Move from processor to case and assemble a configuration that fits the way you work. There is no standard answer, only a more suitable build.', start: 'Start configuring',
    selectComponents: 'SELECT COMPONENTS', back: 'Back to all components', searchCpu: 'Search {count} CPU models', searchGpu: 'Search {count} GPU models', cpuPlaceholder: 'e.g. Ryzen 7 7800X3D or Core i5-14600K', gpuPlaceholder: 'e.g. RTX 5090 D V2, RX 9070 XT, or Arc B580', boardSize: 'Motherboard size',
    choose: 'Choose', chosen: 'Selected', incompatible: 'Incompatible with the selected CPU, motherboard, or memory', memoryIncompatible: 'Incompatible with the selected CPU or motherboard memory generation', memorySlots: 'Check motherboard memory slots', gpuSlots: 'Check motherboard PCIe slots', storagePorts: 'Check motherboard storage ports',
    memoryChosen: '{count} / 4 memory modules selected. {notice}', gpuChosen: '{count} / 4 graphics cards selected. {notice}', storageChosen: 'PCIe {pcie} / 5, SATA + HDD {other}. {notice}', clearMemory: 'Clear memory', clearGpu: 'Clear graphics cards', clearStorage: 'Clear storage', loadMore: 'Load more ({shown} / {total} shown)', noCpu: 'No matching CPU models.', noGpu: 'No matching GPU models.', selectedCount: '{selected} / {total} components selected', continue: 'Continue building', available: 'Available', maxSupport: 'Max support', socket: 'Socket',
    maxGpu: 'You can select up to 4 graphics cards.', maxMemory: 'You can select up to 4 memory modules.', memorySame: '{name} is selected. Memory generation and capacity must match.', maxStorage: 'You can select up to {count} {standard} drives.',
    exportTitle: 'PC Configuration', exportTime: 'Exported', exportEmpty: 'No components selected.', bilingualTitle: 'PC Configuration / 装机配置', bilingualTime: 'Exported / 导出时间', bilingualEmpty: 'No components selected. / 尚未选择任何组件。',
  },
}

const categoryCopy = {
  cpu: { zh: ['CPU', '处理器', '提供 AMD Ryzen 与第五代及以上 Intel Core 消费级处理器。'], en: ['CPU', 'Processor', 'AMD Ryzen and 5th-generation-or-newer Intel Core consumer processors.'] },
  motherboard: { zh: ['主板', '连接平台', '按 CPU 插槽和代际选择消费级主板芯片组。'], en: ['Motherboard', 'Platform', 'Choose consumer motherboard chipsets by CPU socket and generation.'] },
  gpu: { zh: ['显卡', '图形性能', '选择 NVIDIA、AMD Radeon 或 Intel Arc 消费级显卡。'], en: ['Graphics card', 'Graphics', 'Choose NVIDIA, AMD Radeon, or Intel Arc consumer graphics cards.'] },
  memory: { zh: ['内存', '运行内存', '最多选择 4 条内存，注意主板内存代际与插槽数量。'], en: ['Memory', 'System memory', 'Select up to four modules and check the motherboard memory generation and slot count.'] },
  storage: { zh: ['存储', '数据存储', 'PCIe、SATA 与机械硬盘可组合选择，注意主板接口数量。'], en: ['Storage', 'Data storage', 'Combine PCIe, SATA, and hard drives while checking motherboard ports.'] },
  power: { zh: ['电源', '供电方案', '按整机功耗选择供电余量。'], en: ['Power supply', 'Power delivery', 'Choose adequate headroom for total system power draw.'] },
  cooler: { zh: ['散热器', '温度控制', '选择风冷热管方案或一体式水冷排规格。'], en: ['Cooler', 'Thermal control', 'Choose an air-cooler heat-pipe layout or all-in-one liquid radiator size.'] },
  case: { zh: ['机箱', '整机外观', '机箱尺寸决定可容纳的主板规格。'], en: ['Case', 'Enclosure', 'Case size determines the supported motherboard form factor.'] },
}

const productCopy = {
  cooler: {
    '4 热管单塔风冷': { zh: '4 热管单塔风冷', en: '4-heatpipe single-tower air cooler' },
    '4 热管双塔风冷': { zh: '4 热管双塔风冷', en: '4-heatpipe dual-tower air cooler' },
    '6 热管单塔风冷': { zh: '6 热管单塔风冷', en: '6-heatpipe single-tower air cooler' },
    '6 热管双塔风冷': { zh: '6 热管双塔风冷', en: '6-heatpipe dual-tower air cooler' },
    '8 热管单塔风冷': { zh: '8 热管单塔风冷', en: '8-heatpipe single-tower air cooler' },
    '8 热管双塔风冷': { zh: '8 热管双塔风冷', en: '8-heatpipe dual-tower air cooler' },
    '120 水冷': { zh: '120 水冷', en: '120 mm liquid cooler' },
    '240 水冷': { zh: '240 水冷', en: '240 mm liquid cooler' },
    '360 水冷': { zh: '360 水冷', en: '360 mm liquid cooler' },
    '420 水冷': { zh: '420 水冷', en: '420 mm liquid cooler' },
  },
  case: {
    'ITX 机箱': { zh: 'ITX 机箱', en: 'ITX case' },
    'M-ATX 机箱': { zh: 'M-ATX 机箱', en: 'M-ATX case' },
    'ATX 机箱': { zh: 'ATX 机箱', en: 'ATX case' },
    'E-ATX 机箱': { zh: 'E-ATX 机箱', en: 'E-ATX case' },
    '开放式机箱': { zh: '开放式机箱', en: 'Open-frame case' },
  },
}

const language = ref('zh')
const t = (key, values = {}) => (copy[language.value][key] || key).replace(/\{(\w+)\}/g, (_, name) => values[name] ?? '')
const categoryText = (slug, index) => categoryCopy[slug]?.[language.value]?.[index] || ''
const categoryLabel = (slug) => categoryText(slug, 0)
const localizedProductName = (slug, product, locale = language.value) => productCopy[slug]?.[productName(product)]?.[locale] || productName(product)
const bilingualProductName = (slug, product) => productCopy[slug]?.[productName(product)] ? `${localizedProductName(slug, product, 'en')} / ${localizedProductName(slug, product, 'zh')}` : productName(product)
const setLanguage = () => {
  language.value = language.value === 'zh' ? 'en' : 'zh'
  memoryNotice.value = ''
  gpuNotice.value = ''
  storageNotice.value = ''
}

watch(language, (value) => {
  document.documentElement.lang = value === 'zh' ? 'zh-CN' : 'en'
})

function isSupportedIntelCpu(model) {
  if (model.startsWith('Intel Core Ultra')) return true
  const match = model.match(/^Intel Core i[3579]-(\d+)/)
  if (!match) return false
  const modelNumber = match[1]
  const generation = modelNumber.length === 4 ? Number(modelNumber[0]) : Number(modelNumber.slice(0, 2))
  return generation >= 5 && !/-\d+(?:X|XE)$/.test(model)
}

const consumerCpuModels = cpuModels.filter((model) => model.startsWith('AMD Ryzen') || isSupportedIntelCpu(model))
const pcieCapacities = ['256GB', '512GB', '1TB', '2TB', '4TB', '8TB']
const sataCapacities = ['256GB', '512GB', '1TB', '2TB', '4TB', '8TB', '12TB', '16TB']
const hddCapacities = ['256GB', '512GB', '1TB', '2TB', '4TB', '8TB', '12TB', '16TB', '24TB']
const storageProducts = [
  ...['PCIe 3.0', 'PCIe 4.0', 'PCIe 5.0'].flatMap((standard) => pcieCapacities.map((capacity) => ({ name: `${standard} ${capacity}`, type: 'pcie', standard, capacity }))),
  ...sataCapacities.map((capacity) => ({ name: `SATA SSD ${capacity}`, type: 'sata', standard: 'SATA', capacity })),
  ...hddCapacities.map((capacity) => ({ name: `机械硬盘 ${capacity}`, type: 'hdd', standard: 'HDD', capacity })),
]
const boardSizes = [
  { value: 'ITX', rank: 1 }, { value: 'M-ATX', rank: 2 }, { value: 'ATX', rank: 3 }, { value: 'E-ATX', rank: 4 },
]
const caseProducts = [
  { name: 'ITX 机箱', maxSize: 1 }, { name: 'M-ATX 机箱', maxSize: 2 }, { name: 'ATX 机箱', maxSize: 3 }, { name: 'E-ATX 机箱', maxSize: 4 }, { name: '开放式机箱', maxSize: 4 },
]

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (window.location.hostname === 'localhost' ? '' : 'https://api.pconfig.tkr-studio.com')

const categories = reactive([
  { slug: 'cpu', name: 'CPU', detail: '处理器', mark: 'CPU', tone: 'cyan', intro: '提供 AMD Ryzen 与第五代及以上 Intel Core 消费级处理器。', products: consumerCpuModels },
  { slug: 'motherboard', name: '主板', detail: '连接平台', mark: 'MB', tone: 'lime', intro: '按 CPU 插槽和代际选择消费级主板芯片组。', products: motherboardChipsets },
  { slug: 'gpu', name: '显卡', detail: '图形性能', mark: 'GPU', tone: 'violet', intro: '选择 NVIDIA、AMD Radeon 或 Intel Arc 消费级显卡。', products: gpuModels },
  { slug: 'memory', name: '内存', detail: '运行内存', mark: 'RAM', tone: 'amber', intro: '可选择最多 4 条内存，注意主板的内存代际与插槽数量。', products: [
    { name: 'DDR3 8GB', generation: 'DDR3', capacity: '8GB' }, { name: 'DDR3 16GB', generation: 'DDR3', capacity: '16GB' }, { name: 'DDR3 32GB', generation: 'DDR3', capacity: '32GB' },
    { name: 'DDR4 8GB', generation: 'DDR4', capacity: '8GB' }, { name: 'DDR4 16GB', generation: 'DDR4', capacity: '16GB' }, { name: 'DDR4 24GB', generation: 'DDR4', capacity: '24GB' }, { name: 'DDR4 32GB', generation: 'DDR4', capacity: '32GB' }, { name: 'DDR4 48GB', generation: 'DDR4', capacity: '48GB' }, { name: 'DDR4 128GB', generation: 'DDR4', capacity: '128GB' },
    { name: 'DDR5 8GB', generation: 'DDR5', capacity: '8GB' }, { name: 'DDR5 16GB', generation: 'DDR5', capacity: '16GB' }, { name: 'DDR5 24GB', generation: 'DDR5', capacity: '24GB' }, { name: 'DDR5 32GB', generation: 'DDR5', capacity: '32GB' }, { name: 'DDR5 48GB', generation: 'DDR5', capacity: '48GB' }, { name: 'DDR5 128GB', generation: 'DDR5', capacity: '128GB' },
  ] },
  { slug: 'storage', name: '存储', detail: '数据存储', mark: 'SSD', tone: 'blue', intro: 'PCIe、SATA 与机械硬盘可组合选择，注意主板接口数量。', products: storageProducts },
  { slug: 'power', name: '电源', detail: '供电方案', mark: 'PSU', tone: 'yellow', intro: '按整机功耗选择供电余量。', products: ['250W', '300W', '350W', '400W', '450W', '500W', '550W', '600W', '650W', '700W', '750W', '800W', '850W', '900W', '1000W', '1200W', '1300W', '1500W', '1600W'] },
  { slug: 'cooler', name: '散热器', detail: '温度控制', mark: 'COOL', intro: '选择风冷热管方案或一体式水冷排规格。', tone: 'indigo', products: ['4 热管单塔风冷', '4 热管双塔风冷', '6 热管单塔风冷', '6 热管双塔风冷', '8 热管单塔风冷', '8 热管双塔风冷', '120 水冷', '240 水冷', '360 水冷', '420 水冷'] },
  { slug: 'case', name: '机箱', detail: '整机外观', mark: 'CASE', tone: 'pink', intro: '机箱尺寸决定可容纳的主板规格。', products: caseProducts },
])

const route = ref(window.location.pathname.replace(/^\//, '') || 'home')
const selections = ref({})
const cpuSearch = ref('')
const cpuVisibleCount = ref(50)
const gpuSearch = ref('')
const gpuVisibleCount = ref(50)
const motherboardSize = ref('ATX')
const memoryNotice = ref('')
const gpuNotice = ref('')
const storageNotice = ref('')
const activeCategory = computed(() => categories.find((category) => category.slug === route.value))
const selectedItems = computed(() => Object.values(selections.value))
const cpuResults = computed(() => categories[0].products.filter((model) => model.toLowerCase().includes(cpuSearch.value.trim().toLowerCase())))
const gpuResults = computed(() => categories.find((category) => category.slug === 'gpu').products.filter((model) => model.toLowerCase().includes(gpuSearch.value.trim().toLowerCase())))
const displayedProducts = computed(() => {
  if (activeCategory.value?.slug === 'cpu') return cpuResults.value.slice(0, cpuVisibleCount.value)
  if (activeCategory.value?.slug === 'gpu') return gpuResults.value.slice(0, gpuVisibleCount.value)
  return activeCategory.value?.products || []
})
const memorySelections = computed(() => selections.value.memory?.items || [])
const hasMemorySlotWarning = computed(() => memorySelections.value.length > 2)
const gpuSelections = computed(() => selections.value.gpu?.items || [])
const storageSelections = computed(() => selections.value.storage?.items || [])
const storagePcieCount = computed(() => storageSelections.value.filter((item) => item.type === 'pcie').length)
const storageSataHddCount = computed(() => storageSelections.value.filter((item) => item.type === 'sata' || item.type === 'hdd').length)
const hasGpuSlotWarning = computed(() => gpuSelections.value.length > 2)
const hasStorageSlotWarning = computed(() => storagePcieCount.value > 2 || storageSataHddCount.value > 4)
const selectedBoardSize = computed(() => selections.value.motherboard?.size || '')
const selectedBoardRank = computed(() => boardSizes.find((size) => size.value === selectedBoardSize.value)?.rank || 0)

function cpuCompatibility(model) {
  if (model.startsWith('AMD Ryzen')) {
    const number = model.match(/\d{4}/)?.[0] || '1000'
    return Number(number[0]) >= 7 ? { socket: 'AM5', ddr: ['DDR5'] } : { socket: 'AM4', ddr: ['DDR4'] }
  }
  if (model.startsWith('Intel Core Ultra')) return { socket: 'LGA1851', ddr: ['DDR5'], generation: 20 }
  const number = model.match(/^Intel Core i[3579]-(\d+)/)?.[1] || ''
  const generation = number.length === 4 ? Number(number[0]) : Number(number.slice(0, 2))
  if (generation === 5) return { socket: 'LGA1150', ddr: ['DDR3', 'DDR4'], generation }
  if (generation <= 7) return { socket: 'LGA1151', ddr: ['DDR3', 'DDR4'], generation }
  if (generation <= 9) return { socket: 'LGA1151', ddr: ['DDR4'], generation }
  if (generation <= 11) return { socket: 'LGA1200', ddr: ['DDR4'], generation }
  return { socket: 'LGA1700', ddr: ['DDR4', 'DDR5'], generation }
}

function motherboardSupportsCpu(board, cpuModel) {
  const cpu = cpuCompatibility(cpuModel)
  if (board.socket !== cpu.socket) return false
  if (!board.platform || !cpu.generation) return true
  const range = board.platform.match(/(\d+)(?:th-(\d+)th)?/)
  if (!range) return true
  const min = Number(range[1])
  const max = Number(range[2] || range[1])
  return cpu.generation >= min && cpu.generation <= max
}

function productDisabled(category, product) {
  const selectedCpu = selections.value.cpu?.name
  const selectedBoard = selections.value.motherboard?.product
  const selectedMemory = memorySelections.value[0]
  if (category.slug === 'cpu') return Boolean(selectedBoard && !motherboardSupportsCpu(selectedBoard, product)) || Boolean(selectedMemory && !cpuCompatibility(product).ddr.includes(selectedMemory.generation))
  if (category.slug === 'motherboard') return Boolean(selectedCpu && !motherboardSupportsCpu(product, selectedCpu)) || Boolean(selectedMemory && !product.ddr.includes(selectedMemory.generation))
  if (category.slug === 'memory') return Boolean(selectedCpu && !cpuCompatibility(selectedCpu).ddr.includes(product.generation)) || Boolean(selectedBoard && !selectedBoard.ddr.includes(product.generation))
  if (category.slug === 'case') return selectedBoardRank.value > product.maxSize
  return false
}

function disabledReason(category, product) {
  if (!productDisabled(category, product)) return ''
  if (category.slug === 'memory') return t('memoryIncompatible')
  return t('incompatible')
}

function navigate(path) {
  window.history.pushState({}, '', path)
  route.value = path.replace(/^\//, '') || 'home'
  cpuSearch.value = ''
  cpuVisibleCount.value = 50
  gpuSearch.value = ''
  gpuVisibleCount.value = 50
  memoryNotice.value = ''
  gpuNotice.value = ''
  storageNotice.value = ''
  motherboardSize.value = selections.value.motherboard?.size || 'ATX'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function choose(category, product) {
  if (productDisabled(category, product)) return
  if (category.slug === 'gpu') {
    if (gpuSelections.value.length >= 4) {
      gpuNotice.value = t('maxGpu')
      return
    }
    const items = [...gpuSelections.value, product]
    selections.value = { ...selections.value, gpu: { category: category.name, name: items.map((item) => item).join(' + '), items, price: '' } }
    gpuNotice.value = ''
    return
  }
  if (category.slug === 'storage') {
    const current = storageSelections.value
    const typeCount = current.filter((item) => item.type === product.type).length
    const maxByType = { pcie: 5, sata: 6, hdd: 12 }
    if (typeCount >= maxByType[product.type]) {
      storageNotice.value = t('maxStorage', { standard: product.standard, count: maxByType[product.type] })
      return
    }
    const items = [...current, product]
    selections.value = { ...selections.value, storage: { category: category.name, name: items.map((item) => item.name).join(' + '), items, price: '' } }
    storageNotice.value = ''
    return
  }
  if (category.slug === 'motherboard') {
    const size = motherboardSize.value
    selections.value = { ...selections.value, motherboard: { category: category.name, name: `${product.chipset} / ${size}`, product, size, price: '' } }
    return
  }
  if (category.slug === 'memory') {
    const current = memorySelections.value
    const selectedSpec = current[0]
    if (selectedSpec && selectedSpec.name !== product.name) {
      memoryNotice.value = t('memorySame', { name: selectedSpec.name })
      return
    }
    if (current.length >= 4) {
      memoryNotice.value = t('maxMemory')
      return
    }
    const items = [...current, product]
    selections.value = { ...selections.value, memory: { category: category.name, name: `${product.name} x${items.length}`, items, price: '' } }
    memoryNotice.value = ''
    return
  }
  const name = productName(product)
  selections.value = { ...selections.value, [category.slug]: { category: category.name, name, price: '', product } }
}

function productName(product) {
  return Array.isArray(product) ? product[0] : typeof product === 'string' ? product : product.name || product.chipset
}

function productMeta(product) {
  return typeof product === 'string' ? t('available') : product.generation ? `${product.generation} / ${product.capacity}` : product.type ? `${product.standard} / ${product.capacity}` : product.maxSize ? `${t('maxSupport')} ${boardSizes.find((size) => size.rank === product.maxSize)?.value}` : `${t('socket')} ${product.socket} / ${product.ddr.join(' / ')}`
}

function isProductSelected(category, product) {
  if (category.slug === 'memory') return memorySelections.value[0]?.name === product.name
  if (category.slug === 'gpu') return gpuSelections.value.includes(product)
  if (category.slug === 'storage') return storageSelections.value.some((item) => item.name === product.name)
  if (category.slug === 'motherboard') return selections.value.motherboard?.product?.chipset === product.chipset
  return selections.value[category.slug]?.name === productName(product)
}

function updateMotherboardSize() {
  const selectedBoard = selections.value.motherboard
  if (!selectedBoard) return
  selections.value = { ...selections.value, motherboard: { ...selectedBoard, name: `${selectedBoard.product.chipset} / ${motherboardSize.value}`, size: motherboardSize.value } }
}

function selectedLabel(category) {
  const selection = selections.value[category.slug]
  return selection ? localizedProductName(category.slug, selection.name) : ''
}

function clearMemory() {
  const { memory, ...otherSelections } = selections.value
  selections.value = otherSelections
  memoryNotice.value = ''
}

function clearMultiSelection(categorySlug) {
  const { [categorySlug]: ignored, ...otherSelections } = selections.value
  selections.value = otherSelections
  if (categorySlug === 'gpu') gpuNotice.value = ''
  if (categorySlug === 'storage') storageNotice.value = ''
}

function clearConfiguration() {
  selections.value = {}
  memoryNotice.value = ''
  motherboardSize.value = 'ATX'
}

function downloadConfiguration(lines, filename) {
  const url = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

function exportConfiguration() {
  const locale = language.value === 'zh' ? 'zh-CN' : 'en-US'
  const lines = [t('exportTitle'), `${t('exportTime')}: ${new Date().toLocaleString(locale)}`, '']
  if (!selectedItems.value.length) lines.push(t('exportEmpty'))
  selectedItems.value.forEach((item) => {
    const slug = Object.keys(selections.value).find((key) => selections.value[key] === item)
    lines.push(`${categoryLabel(slug) || item.category}: ${localizedProductName(slug, item.name)}`)
  })
  downloadConfiguration(lines, language.value === 'zh' ? '装机配置.txt' : 'pc-configuration.txt')
}

function exportBilingualConfiguration() {
  const lines = [t('bilingualTitle'), `${t('bilingualTime')}: ${new Date().toLocaleString('zh-CN')}`, '']
  if (!selectedItems.value.length) lines.push(t('bilingualEmpty'))
  selectedItems.value.forEach((item) => {
    const slug = Object.keys(selections.value).find((key) => selections.value[key] === item)
    lines.push(`${categoryCopy[slug]?.en?.[0] || item.category} / ${categoryCopy[slug]?.zh?.[0] || item.category}: ${bilingualProductName(slug, item.name)}`)
  })
  downloadConfiguration(lines, 'pc-configuration-bilingual.txt')
}

function handlePopState() {
  route.value = window.location.pathname.replace(/^\//, '') || 'home'
}

function apiProduct(component) {
  if (component.category === 'motherboard') return { chipset: component.name, ...component.attributes }
  if (component.category === 'memory' || component.category === 'storage' || component.category === 'case') return { name: component.name, ...component.attributes }
  return component.name
}

async function loadComponents() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/components/`)
    if (!response.ok) throw new Error('组件 API 请求失败')
    const { results } = await response.json()
    const byCategory = Object.groupBy(results, (component) => component.category)
    categories.forEach((category) => {
      if (byCategory[category.slug]?.length) category.products = byCategory[category.slug].map(apiProduct)
    })
  } catch (error) {
    console.warn('无法加载后端组件数据，继续使用本地数据。', error)
  }
}

onMounted(() => {
  window.addEventListener('popstate', handlePopState)
  loadComponents()
})
onUnmounted(() => window.removeEventListener('popstate', handlePopState))
</script>

<template>
  <main class="site-shell">
    <header class="topbar">
      <button class="brand" :aria-label="t('back')" @click="navigate('/')"><span class="brand-dot"></span>BUILD/FORM</button>
      <div class="header-actions">
        <button class="header-text-button" @click="setLanguage">{{ t('switchLanguage') }}</button>
        <a class="header-text-button" href="https://tkr-studio.com/" target="_blank" rel="noopener noreferrer">{{ t('checkIngredients') }}</a>
        <button class="header-text-button" @click="clearConfiguration">{{ t('clear') }}</button>
        <button class="header-text-button" @click="exportConfiguration">{{ t('export') }}</button>
        <button class="header-text-button" @click="exportBilingualConfiguration">{{ t('bilingualExport') }}</button>
        <button class="summary-button" @click="document.getElementById('workspace')?.scrollIntoView({ behavior: 'smooth' })">{{ t('selected') }} {{ selectedItems.length }} {{ t('item') }}</button>
      </div>
    </header>

    <template v-if="!activeCategory">
      <section class="intro">
        <p class="eyebrow">PERSONAL COMPUTER CONFIGURATOR</p>
        <h1>{{ t('heroTitle') }}<br><i>{{ t('heroSubtitle') }}</i></h1>
        <p class="intro-copy">{{ t('heroCopy') }}</p>
        <a class="text-link" href="#workspace">{{ t('start') }} <span>↓</span></a>
      </section>

      <section id="workspace" class="workspace">
        <div class="section-heading"><p class="eyebrow">01 / {{ t('selectComponents') }}</p></div>
        <div class="component-grid">
          <button v-for="(category, index) in categories" :key="category.slug" class="component-card" :class="category.tone" @click="navigate(`/${category.slug}`)">
            <span class="card-number">0{{ index + 1 }}</span><span class="hardware-mark">{{ category.mark }}</span>
            <span class="card-title">{{ categoryLabel(category.slug) }}</span><span class="card-detail">{{ categoryText(category.slug, 1) }}</span><span class="card-arrow">↗</span>
            <span v-if="selectedLabel(category)" class="card-selection">{{ selectedLabel(category) }}</span>
            <span v-if="category.slug === 'memory' && hasMemorySlotWarning" class="memory-card-warning">{{ t('memorySlots') }}</span>
            <span v-if="category.slug === 'gpu' && hasGpuSlotWarning" class="memory-card-warning">{{ t('gpuSlots') }}</span>
            <span v-if="category.slug === 'storage' && hasStorageSlotWarning" class="memory-card-warning">{{ t('storagePorts') }}</span>
          </button>
        </div>
      </section>

    </template>

    <template v-else>
      <section class="detail-page">
        <button class="back-button" @click="navigate('/')">← {{ t('back') }}</button>
        <p class="eyebrow">COMPONENT / {{ activeCategory.mark }}</p>
        <div class="detail-heading"><div><h1>{{ categoryLabel(activeCategory.slug) }}<small>{{ categoryText(activeCategory.slug, 1) }}</small></h1><p>{{ categoryText(activeCategory.slug, 2) }}</p></div><div class="detail-mark" :class="activeCategory.tone">{{ activeCategory.mark }}</div></div>
        <div v-if="activeCategory.slug === 'cpu'" class="cpu-tools">
          <label for="cpu-search">{{ t('searchCpu', { count: categories[0].products.length }) }}</label>
          <input id="cpu-search" v-model="cpuSearch" type="search" :placeholder="t('cpuPlaceholder')" @input="cpuVisibleCount = 50">
        </div>
        <div v-if="activeCategory.slug === 'gpu'" class="cpu-tools">
          <label for="gpu-search">{{ t('searchGpu', { count: gpuModels.length }) }}</label>
          <input id="gpu-search" v-model="gpuSearch" type="search" :placeholder="t('gpuPlaceholder')" @input="gpuVisibleCount = 50">
        </div>
        <div v-if="activeCategory.slug === 'motherboard'" class="size-control">
          <label for="motherboard-size">{{ t('boardSize') }}</label>
          <select id="motherboard-size" v-model="motherboardSize" @change="updateMotherboardSize">
            <option v-for="size in boardSizes" :key="size.value" :value="size.value" :disabled="selections.case && size.rank > selections.case.product.maxSize">{{ size.value }}</option>
          </select>
        </div>
        <div class="product-list">
          <button v-for="product in displayedProducts" :key="productName(product)" class="product-row" :class="{ selected: isProductSelected(activeCategory, product), disabled: productDisabled(activeCategory, product) }" :disabled="productDisabled(activeCategory, product)" @click="choose(activeCategory, product)">
            <span class="product-name">{{ localizedProductName(activeCategory.slug, product) }}</span><span class="product-price">{{ productMeta(product) }}</span><span class="select-state">{{ productDisabled(activeCategory, product) ? disabledReason(activeCategory, product) : isProductSelected(activeCategory, product) ? t('chosen') : t('choose') }}</span>
          </button>
        </div>
        <div v-if="activeCategory.slug === 'memory'" class="memory-selection-info"><span>{{ t('memoryChosen', { count: memorySelections.length, notice: memoryNotice }) }}</span><button v-if="memorySelections.length" @click="clearMemory">{{ t('clearMemory') }}</button></div>
        <div v-if="activeCategory.slug === 'gpu'" class="memory-selection-info"><span>{{ t('gpuChosen', { count: gpuSelections.length, notice: gpuNotice }) }}</span><button v-if="gpuSelections.length" @click="clearMultiSelection('gpu')">{{ t('clearGpu') }}</button></div>
        <div v-if="activeCategory.slug === 'storage'" class="memory-selection-info"><span>{{ t('storageChosen', { pcie: storagePcieCount, other: storageSataHddCount, notice: storageNotice }) }}</span><button v-if="storageSelections.length" @click="clearMultiSelection('storage')">{{ t('clearStorage') }}</button></div>
        <button v-if="activeCategory.slug === 'cpu' && cpuVisibleCount < cpuResults.length" class="load-more" @click="cpuVisibleCount += 50">{{ t('loadMore', { shown: displayedProducts.length, total: cpuResults.length }) }}</button>
        <button v-if="activeCategory.slug === 'gpu' && gpuVisibleCount < gpuResults.length" class="load-more" @click="gpuVisibleCount += 50">{{ t('loadMore', { shown: displayedProducts.length, total: gpuResults.length }) }}</button>
        <p v-else-if="activeCategory.slug === 'cpu' && !cpuResults.length" class="empty-state">{{ t('noCpu') }}</p>
        <p v-else-if="activeCategory.slug === 'gpu' && !gpuResults.length" class="empty-state">{{ t('noGpu') }}</p>
        <div class="next-control"><span>{{ t('selectedCount', { selected: selectedItems.length, total: categories.length }) }}</span><button @click="navigate('/')">{{ t('continue') }} →</button></div>
      </section>
    </template>
  </main>
</template>
